import enum
import asyncio
import struct
import math
from PIL import Image, ImageOps
from .exception import BLEException, PrinterException
from .bluetooth import BLETransport
from .logger_config import get_logger
from .packet import NiimbotPacket, packet_to_int

from devtools import debug

logger = get_logger()


class InfoEnum(enum.IntEnum):
    DENSITY = 1
    PRINTSPEED = 2
    LABELTYPE = 3
    LANGUAGETYPE = 6
    AUTOSHUTDOWNTIME = 7
    DEVICETYPE = 8
    SOFTVERSION = 9
    BATTERY = 10
    DEVICESERIAL = 11
    HARDVERSION = 12


class RequestCodeEnum(enum.IntEnum):
    GET_INFO = 64  # 0x40
    GET_RFID = 26  # 0x1A
    HEARTBEAT = 220  # 0xDC
    SET_LABEL_TYPE = 35  # 0x23
    SET_LABEL_DENSITY = 33  # 0x21
    START_PRINT = 1  # 0x01
    END_PRINT = 243  # 0xF3
    START_PAGE_PRINT = 3  # 0x03
    END_PAGE_PRINT = 227  # 0xE3
    ALLOW_PRINT_CLEAR = 32  # 0x20
    SET_DIMENSION = 19  # 0x13
    SET_QUANTITY = 21  # 0x15
    GET_PRINT_STATUS = 163  # 0xA3
    CONNECT = 0xC1


class PrinterClient:
    def __init__(self, device):
        self.char_uuid = None
        self.device = device
        self.transport = BLETransport()
        self.notification_event = asyncio.Event()
        self.notification_data = None

    async def connect(self):
        # Pass BLEDevice (not just address) for more reliable BlueZ connections.
        if await self.transport.connect(self.device):
            if not self.char_uuid:
                await self.find_characteristics()
            logger.info(f"Successfully connected to {self.device.name}")
            return True
        logger.error("Connection failed.")
        return False

    async def disconnect(self):
        await self.transport.disconnect()
        logger.info(f"Printer {self.device.name} disconnected.")

    async def find_characteristics(self):
        services = {}
        for service in self.transport.client.services:
            s = []
            for char in service.characteristics:
                s.append({
                    "id": char.uuid,
                    "handle": char.handle,
                    "properties": char.properties
                })

            services[service.uuid] = s

        for service_id, characteristics in services.items():
            if len(characteristics) == 1:  # Check if there's exactly one characteristic
                props = characteristics[0]['properties']
                if 'read' in props and 'write-without-response' in props and 'notify' in props:
                    self.char_uuid = characteristics[0]['id']  # Return the service ID that meets the criteria
        if not self.char_uuid:
            raise PrinterException("Cannot find bluetooth characteristics.")

    async def send_command(self, request_code, data, timeout=5):
        if not self.transport.client or not self.transport.client.is_connected:
            await self.connect()
        packet = NiimbotPacket(request_code, data)
        self.notification_event.clear()
        self.notification_data = None
        try:
            await self.transport.start_notification(self.char_uuid, self.notification_handler)
            await self.transport.write(packet.to_bytes(), self.char_uuid)
            logger.debug(f"Printer command sent - {RequestCodeEnum(request_code).name}")
            await asyncio.wait_for(self.notification_event.wait(), timeout)
            if not self.notification_data:
                return None
            return NiimbotPacket.from_bytes(self.notification_data)
        except asyncio.TimeoutError:
            logger.error(f"Timeout occurred for request {RequestCodeEnum(request_code).name}")
            return None
        except BLEException as e:
            logger.error(f"An error occurred: {e}")
            return None
        finally:
            # Always stop notify — leaving it on breaks bulk bitmap writes / hangs finish.
            try:
                await self.transport.stop_notification(self.char_uuid)
            except Exception:
                pass
            self.notification_event.clear()

    async def write_raw(self, data):
        try:
            if not self.transport.client or not self.transport.client.is_connected:
                await self.connect()
            await self.transport.write(data.to_bytes(), self.char_uuid)
        except BLEException as e:
            logger.error(f"An error occurred: {e}")

    async def write_no_notify(self, request_code, data):
        try:
            if not self.transport.client or not self.transport.client.is_connected:
                await self.connect()
            packet = NiimbotPacket(request_code, data)
            await self.transport.write(packet.to_bytes(), self.char_uuid)
        except BLEException as e:
            logger.error(f"An error occurred: {e}")

    def notification_handler(self, sender, data):
        logger.trace(f"Notification: {data}")
        self.notification_data = data
        self.notification_event.set()

    async def print_image(self, image: Image, density: int = 3, quantity: int = 1, vertical_offset= 0,
                          horizontal_offset = 0, *, invert: bool = True, use_print_clear: bool = False,
                          page_size_6b: bool = False):
        """Print path for D110 / B21 / B21S family.

        B21S requires 6-byte SetPageSize (rows, cols, copies). Using 4-byte page size
        makes the printer feed a blank label (AndBondStyle/niimprint#33).
        """
        try:
            await self.handshake_connect()
        except Exception as e:
            logger.debug(f"Connect handshake skipped: {e}")

        await self.set_label_density(density)
        await self.set_label_type(1)
        await self.start_print()
        if use_print_clear:
            try:
                await self.allow_print_clear()
            except Exception as e:
                logger.debug(f"Print clear skipped: {e}")
        await self.start_page_print()

        # Critical for B21S: 6-byte dimension includes quantity/copies
        if page_size_6b:
            await self.set_dimension_v2(image.height, image.width, quantity)
        else:
            await self.set_dimension(image.height, image.width)
            await self.set_quantity(quantity)

        try:
            await self.transport.stop_notification(self.char_uuid)
        except Exception:
            pass

        row_count = 0
        for pkt in self._encode_image(image, vertical_offset, horizontal_offset, invert=invert):
            await self.write_raw(pkt)
            row_count += 1
            await asyncio.sleep(0.01)
        logger.info(f"Sent {row_count} bitmap rows (invert={invert}, page_size_6b={page_size_6b})")

        # Allow paper advance before polling
        await asyncio.sleep(0.5)

        ok = False
        for _ in range(10):
            packet = await self.send_command(RequestCodeEnum.END_PAGE_PRINT, b"\x01", timeout=2)
            if packet and packet.data and packet.data[0]:
                ok = True
                break
            await asyncio.sleep(0.1)
        if not ok:
            logger.warning("end_page_print did not ACK — continuing")

        for _ in range(40):
            status = await self.get_print_status_quick()
            if status and status.get("page") >= quantity:
                break
            await asyncio.sleep(0.15)

        packet = await self.send_command(RequestCodeEnum.END_PRINT, b"\x01", timeout=2)
        if not packet:
            logger.warning("end_print did not ACK")

    async def get_print_status_quick(self):
        packet = await self.send_command(RequestCodeEnum.GET_PRINT_STATUS, b"\x01", timeout=2)
        if not packet or not packet.data or len(packet.data) < 4:
            return None
        page, progress1, progress2 = struct.unpack(">HBB", packet.data[:4])
        return {"page": page, "progress1": progress1, "progress2": progress2}

    async def print_image_v2(self, image: Image, density: int = 3, quantity: int = 1,
                            vertical_offset=0, horizontal_offset=0):
        """B1 protocol (niimbluelib B1PrintTask): 7-byte PrintStart + 6-byte SetPageSize.

        Fixes from PR #6 review (MultiMote / hadess):
        - total page count in PrintStart must equal quantity (not hardcoded 1)
        - SetPageSize copies field must match quantity for multi-copy jobs
        """
        await self.set_label_density(density)
        await self.set_label_type(1)
        await self.start_print_v2(quantity=quantity)
        await self.start_page_print()
        await self.set_dimension_v2(image.height, image.width, quantity)

        for pkt in self._encode_image(image, vertical_offset, horizontal_offset):
            await self.write_raw(pkt)
            await asyncio.sleep(0.015)

        for _ in range(40):
            try:
                if await self.end_page_print():
                    break
            except Exception as e:
                logger.debug(f"end_page_print: {e}")
            await asyncio.sleep(0.05)

        # Give B1 time to finish multi-copy jobs before tearing down BLE.
        await asyncio.sleep(0.5 + 0.4 * max(0, quantity - 1))

        for _ in range(100):
            try:
                status = await self.get_print_status()
                if status and status.get("page") == quantity:
                    break
            except Exception as e:
                logger.debug(f"get_print_status: {e}")
                break
            await asyncio.sleep(0.1)

        try:
            await self.end_print()
        except Exception as e:
            logger.debug(f"end_print: {e}")

    # Backwards-compatible alias used by PR #6 / older callers
    print_imageV2 = print_image_v2

    async def print_for_model(self, model: str, image: Image, density: int = 3, quantity: int = 1,
                             vertical_offset=0, horizontal_offset=0):
        """Dispatch to the correct print protocol for the selected model."""
        from .models import uses_b1_protocol, uses_page_size_6b
        if uses_b1_protocol(model):
            await self.print_image_v2(image, density=density, quantity=quantity,
                                     vertical_offset=vertical_offset,
                                     horizontal_offset=horizontal_offset)
        else:
            await self.print_image(
                image,
                density=density,
                quantity=quantity,
                vertical_offset=vertical_offset,
                horizontal_offset=horizontal_offset,
                page_size_6b=uses_page_size_6b(model),
            )

    async def handshake_connect(self):
        """Send Connect (0xC1) with 0x03 prefix to reset printer print state."""
        packet = await self.send_command(RequestCodeEnum.CONNECT, b"\x01", timeout=3)
        return packet is not None

    def _encode_image(self, image: Image, vertical_offset=0, horizontal_offset=0, invert: bool = True):
        """Encode image rows for PrintBitmapRow (0x85).

        Matches AndBondStyle/niimprint: invert so black→bit1, counts can be zeros.
        """
        gray = image.convert("L")
        if invert:
            gray = ImageOps.invert(gray)
        img = gray.convert("1", dither=Image.Dither.NONE)

        if horizontal_offset > 0:
            img = ImageOps.expand(img, border=(horizontal_offset, 0, 0, 0), fill=1)
        else:
            img = img.crop((-horizontal_offset, 0, img.width, img.height))

        img = ImageOps.expand(img, border=(0, vertical_offset, 0, 0), fill=1)

        if img.width % 8 != 0:
            pad = 8 - (img.width % 8)
            img = ImageOps.expand(img, border=(0, 0, pad, 0), fill=1)

        for y in range(img.height):
            bitstring = "".join("0" if img.getpixel((x, y)) == 0 else "1" for x in range(img.width))
            payload = int(bitstring, 2).to_bytes(img.width // 8, "big")
            # Zeros are accepted by B21/B21S firmware (AndBondStyle)
            header = struct.pack(">H3BB", y, 0, 0, 0, 1)
            yield NiimbotPacket(0x85, header + payload)

    async def get_info(self, key):
        response = await self.send_command(RequestCodeEnum.GET_INFO, bytes((key,)))

        match key:
            case InfoEnum.DEVICESERIAL:
                return response.data.hex()
            case InfoEnum.SOFTVERSION:
                return packet_to_int(response) / 100
            case InfoEnum.HARDVERSION:
                return packet_to_int(response) / 100
            case _:
                return packet_to_int(response)

        return None

    async def get_rfid(self):
        packet = await self.send_command(RequestCodeEnum.GET_RFID, b"\x01")
        data = packet.data

        if data[0] == 0:
            return None
        uuid = data[0:8].hex()
        idx = 8

        barcode_len = data[idx]
        idx += 1
        barcode = data[idx: idx + barcode_len].decode()

        idx += barcode_len
        serial_len = data[idx]
        idx += 1
        serial = data[idx: idx + serial_len].decode()

        idx += serial_len
        total_len, used_len, type_ = struct.unpack(">HHB", data[idx:])
        return {
            "uuid": uuid,
            "barcode": barcode,
            "serial": serial,
            "used_len": used_len,
            "total_len": total_len,
            "type": type_,
        }

    async def heartbeat(self):
        packet = await self.send_command(RequestCodeEnum.HEARTBEAT, b"\x01")
        closing_state = None
        power_level = None
        paper_state = None
        rfid_read_state = None

        match len(packet.data):
            case 20:
                paper_state = packet.data[18]
                rfid_read_state = packet.data[19]
            case 13:
                closing_state = packet.data[9]
                power_level = packet.data[10]
                paper_state = packet.data[11]
                rfid_read_state = packet.data[12]
            case 19:
                closing_state = packet.data[15]
                power_level = packet.data[16]
                paper_state = packet.data[17]
                rfid_read_state = packet.data[18]
            case 10:
                closing_state = packet.data[8]
                power_level = packet.data[9]
                rfid_read_state = packet.data[8]
            case 9:
                closing_state = packet.data[8]

        return {
            "closing_state": closing_state,
            "power_level": power_level,
            "paper_state": paper_state,
            "rfid_read_state": rfid_read_state,
        }

    async def set_label_type(self, n):
        assert 1 <= n <= 3
        packet = await self.send_command(RequestCodeEnum.SET_LABEL_TYPE, bytes((n,)))
        return bool(packet and packet.data and packet.data[0])

    async def set_label_density(self, n):
        assert 1 <= n <= 5  # B21 has 5 levels, not sure for D11
        packet = await self.send_command(RequestCodeEnum.SET_LABEL_DENSITY, bytes((n,)))
        return bool(packet and packet.data and packet.data[0])

    async def start_print(self):
        packet = await self.send_command(RequestCodeEnum.START_PRINT, b"\x01")
        return bool(packet and packet.data and packet.data[0])

    async def start_print_v2(self, quantity: int):
        """B1 / newer printers: 7-byte PrintStart (big-endian page count + padding + color).

        Wire format (niimbluelib printStart7b):
          u16be total_pages | 0x00 0x00 0x00 0x00 | page_color
        """
        assert 1 <= quantity <= 65535
        payload = struct.pack(">H", quantity) + b"\x00\x00\x00\x00\x00"
        packet = await self.send_command(RequestCodeEnum.START_PRINT, payload)
        return bool(packet and packet.data and packet.data[0])

    start_printV2 = start_print_v2

    async def end_print(self):
        packet = await self.send_command(RequestCodeEnum.END_PRINT, b"\x01")
        return bool(packet and packet.data and packet.data[0])

    async def start_page_print(self):
        packet = await self.send_command(RequestCodeEnum.START_PAGE_PRINT, b"\x01")
        return bool(packet and packet.data and packet.data[0])

    async def end_page_print(self):
        packet = await self.send_command(RequestCodeEnum.END_PAGE_PRINT, b"\x01")
        return bool(packet and packet.data and packet.data[0])

    async def allow_print_clear(self):
        packet = await self.send_command(RequestCodeEnum.ALLOW_PRINT_CLEAR, b"\x01")
        return bool(packet and packet.data and packet.data[0])

    async def set_dimension(self, w, h):
        packet = await self.send_command(
            RequestCodeEnum.SET_DIMENSION, struct.pack(">HH", w, h)
        )
        return bool(packet and packet.data and packet.data[0])

    async def set_dimension_v2(self, w, h, copies):
        """B1: 6-byte SetPageSize (rows, cols, copies) — copies must match quantity."""
        assert 1 <= copies <= 65535
        packet = await self.send_command(
            RequestCodeEnum.SET_DIMENSION, struct.pack(">HHH", w, h, copies)
        )
        return bool(packet and packet.data and packet.data[0])

    set_dimensionV2 = set_dimension_v2

    async def set_quantity(self, n):
        packet = await self.send_command(RequestCodeEnum.SET_QUANTITY, struct.pack(">H", n))
        return bool(packet and packet.data and packet.data[0])

    async def get_print_status(self):
        packet = await self.send_command(RequestCodeEnum.GET_PRINT_STATUS, b"\x01")
        if not packet or not packet.data or len(packet.data) < 4:
            return None
        page, progress1, progress2 = struct.unpack(">HBB", packet.data[:4])
        return {"page": page, "progress1": progress1, "progress2": progress2}

    def __del__(self):
        if self.transport.client.is_connected:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.disconnect())
            else:
                loop.run_until_complete(self.disconnect())
