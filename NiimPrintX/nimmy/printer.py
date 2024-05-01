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


class PrinterClient:
    def __init__(self, device):
        self.char_uuid = None
        self.device = device
        self.transport = BLETransport()
        self.notification_event = asyncio.Event()
        self.notification_data = None

    async def connect(self):
        if await self.transport.connect(self.device.address):
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

    async def send_command(self, request_code, data, timeout=10):
        try:
            if not self.transport.client or not self.transport.client.is_connected:
                await self.connect()
            packet = NiimbotPacket(request_code, data)
            await self.transport.start_notification(self.char_uuid, self.notification_handler)
            await self.transport.write(packet.to_bytes(), self.char_uuid)
            logger.debug(f"Printer command sent - {RequestCodeEnum(request_code).name}")
            await asyncio.wait_for(self.notification_event.wait(), timeout)  # Wait until the notification event is set
            response = NiimbotPacket.from_bytes(self.notification_data)
            await self.transport.stop_notification(self.char_uuid)
            self.notification_event.clear()  # Reset the event for the next notification
            return response
        except asyncio.TimeoutError:
            logger.error(f"Timeout occurred for request {RequestCodeEnum(request_code).name}")
        except BLEException as e:
            logger.error(f"An error occurred: {e}")

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
        # print(f"Notification from {sender}: {data}")
        logger.trace(f"Notification: {data}")
        self.notification_data = data
        self.notification_event.set()

    async def print_image(self, image: Image, density: int = 3, quantity: int = 1):
        await self.set_label_density(density)
        await self.set_label_type(1)
        await self.start_print()
        await self.start_page_print()
        await self.set_dimension(image.height, image.width)
        await self.set_quantity(quantity)

        for pkt in self._encode_image(image):
            # Send each line and wait for a response or status check
            await self.write_raw(pkt)
            # Adding a short delay or status check here can help manage buffer issues
            await asyncio.sleep(0.01)  # Adjust the delay as needed based on printer feedback

        while not await self.end_page_print():
            await asyncio.sleep(0.05)

        while True:
            status = await self.get_print_status()
            if status['page'] == quantity:
                break
            await asyncio.sleep(0.1)

        await self.end_print()

    def _encode_image(self, image: Image):
        img = ImageOps.invert(image.convert("L")).convert("1")
        for y in range(img.height):
            line_data = [img.getpixel((x, y)) for x in range(img.width)]
            line_data = "".join("0" if pix == 0 else "1" for pix in line_data)
            line_data = int(line_data, 2).to_bytes(math.ceil(img.width / 8), "big")
            counts = (0, 0, 0)  # It seems like you can always send zeros
            header = struct.pack(">H3BB", y, *counts, 1)
            pkt = NiimbotPacket(0x85, header + line_data)
            yield pkt

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
        return bool(packet.data[0])

    async def set_label_density(self, n):
        assert 1 <= n <= 5  # B21 has 5 levels, not sure for D11
        packet = await self.send_command(RequestCodeEnum.SET_LABEL_DENSITY, bytes((n,)))
        return bool(packet.data[0])

    async def start_print(self):
        packet = await self.send_command(RequestCodeEnum.START_PRINT, b"\x01")
        return bool(packet.data[0])

    async def end_print(self):
        packet = await self.send_command(RequestCodeEnum.END_PRINT, b"\x01")
        return bool(packet.data[0])

    async def start_page_print(self):
        packet = await self.send_command(RequestCodeEnum.START_PAGE_PRINT, b"\x01")
        return bool(packet.data[0])

    async def end_page_print(self):
        packet = await self.send_command(RequestCodeEnum.END_PAGE_PRINT, b"\x01")
        return bool(packet.data[0])

    async def allow_print_clear(self):
        packet = await self.send_command(RequestCodeEnum.ALLOW_PRINT_CLEAR, b"\x01")
        return bool(packet.data[0])

    async def set_dimension(self, w, h):
        packet = await self.send_command(
            RequestCodeEnum.SET_DIMENSION, struct.pack(">HH", w, h)
        )
        return bool(packet.data[0])

    async def set_quantity(self, n):
        packet = await self.send_command(RequestCodeEnum.SET_QUANTITY, struct.pack(">H", n))
        return bool(packet.data[0])

    async def get_print_status(self):
        packet = await self.send_command(RequestCodeEnum.GET_PRINT_STATUS, b"\x01")
        page, progress1, progress2 = struct.unpack(">HBB", packet.data)
        return {"page": page, "progress1": progress1, "progress2": progress2}

    def __del__(self):
        if self.transport.client.is_connected:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                loop.create_task(self.disconnect())
            else:
                loop.run_until_complete(self.disconnect())
