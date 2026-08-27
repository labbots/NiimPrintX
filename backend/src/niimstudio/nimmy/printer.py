import asyncio
import enum
import math
import struct
from collections import deque

from PIL import Image, ImageOps

from .bluetooth import BLETransport
from .exception import BLEException, PrinterException
from .logger_config import get_logger
from .packet import MAX_PAYLOAD_LENGTH, PACKET_HEADER, PACKET_OVERHEAD, NiimbotPacket, packet_to_int

PRINT_JOB_TIMEOUT_SECONDS = 120.0
PRINT_POLL_INTERVAL_SECONDS = 0.05
PRINT_CLEANUP_TIMEOUT_SECONDS = 10.0
MAX_PROTOCOL_VALUE = 65535
RASTER_HEADER_FORMAT = ">H3BB"
RASTER_HEADER_SIZE = struct.calcsize(RASTER_HEADER_FORMAT)
MAX_RASTER_WIDTH = (MAX_PAYLOAD_LENGTH - RASTER_HEADER_SIZE) * 8

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
        self.command_lock = asyncio.Lock()
        self.notification_event = asyncio.Event()
        self.notification_buffer = bytearray()
        self.notification_packets = deque()
        self.notification_error: PrinterException | None = None

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
        candidates = []
        for service in self.transport.client.services:
            for char in service.characteristics:
                properties = set(char.properties)
                if {"read", "write-without-response", "notify"} <= properties:
                    candidates.append(char.uuid)

        if len(candidates) != 1:
            raise PrinterException("Cannot find bluetooth characteristics.")
        self.char_uuid = candidates[0]

    async def send_command(self, request_code, data, timeout=10, response_offset=1):
        async with self.command_lock:
            notification_started = False
            primary_error: BaseException | None = None
            self.notification_buffer.clear()
            self.notification_packets.clear()
            self.notification_error = None
            self.notification_event.clear()
            try:
                if not self.transport.client or not self.transport.client.is_connected:
                    if not await self.connect():
                        raise PrinterException("Printer connection failed")
                packet = NiimbotPacket(request_code, data)
                await self.transport.start_notification(self.char_uuid, self.notification_handler)
                notification_started = True
                await self.transport.write(packet.to_bytes(), self.char_uuid)
                logger.debug("Printer command sent - {}", RequestCodeEnum(request_code).name)
                expected_response = (int(request_code) + response_offset) & 0xFF
                return await self._wait_for_response(expected_response, timeout)
            except TimeoutError as exception:
                request_name = RequestCodeEnum(request_code).name
                primary_error = PrinterException(f"Printer command {request_name} timed out")
                raise primary_error from exception
            except BLEException as exception:
                primary_error = PrinterException("Bluetooth communication failed")
                raise primary_error from exception
            except BaseException as exception:
                primary_error = exception
                raise
            finally:
                if notification_started and self.transport.client and self.transport.client.is_connected:
                    try:
                        await self.transport.stop_notification(self.char_uuid)
                    except BLEException as exception:
                        if primary_error is None:
                            raise PrinterException("Failed to stop printer notifications") from exception
                        logger.warning("Failed to stop printer notifications after command failure: {}", exception)
                self.notification_event.clear()

    async def _wait_for_response(self, expected_response: int, timeout: float) -> NiimbotPacket:
        loop = asyncio.get_running_loop()
        deadline = loop.time() + timeout
        while True:
            while self.notification_packets:
                packet = self.notification_packets.popleft()
                if packet.type == 0x00:
                    raise PrinterException("Printer does not support this command")
                if packet.type == 0xDB:
                    raise PrinterException("Printer returned an error response")
                if packet.type == expected_response:
                    return packet
                logger.debug(
                    "Ignoring printer response 0x{:02x}; expected 0x{:02x}",
                    packet.type,
                    expected_response,
                )
            if self.notification_error is not None:
                raise self.notification_error

            remaining = deadline - loop.time()
            if remaining <= 0:
                raise TimeoutError
            self.notification_event.clear()
            if self.notification_packets or self.notification_error is not None:
                continue
            await asyncio.wait_for(self.notification_event.wait(), remaining)

    async def write_raw(self, data):
        if not self.transport.client or not self.transport.client.is_connected:
            if not await self.connect():
                raise PrinterException("Printer connection failed")
        try:
            await self.transport.write(data.to_bytes(), self.char_uuid)
        except BLEException as exception:
            raise PrinterException("Bluetooth communication failed") from exception

    async def write_no_notify(self, request_code, data):
        if not self.transport.client or not self.transport.client.is_connected:
            if not await self.connect():
                raise PrinterException("Printer connection failed")
        packet = NiimbotPacket(request_code, data)
        try:
            await self.transport.write(packet.to_bytes(), self.char_uuid)
        except BLEException as exception:
            raise PrinterException("Bluetooth communication failed") from exception

    def notification_handler(self, sender, data):
        logger.trace("Notification: {}", data)
        self.notification_buffer.extend(data)
        while True:
            packet_start = self.notification_buffer.find(PACKET_HEADER)
            if packet_start < 0:
                if self.notification_buffer[-1:] == PACKET_HEADER[:1]:
                    self.notification_buffer[:] = PACKET_HEADER[:1]
                else:
                    self.notification_buffer.clear()
                return
            if packet_start > 0:
                del self.notification_buffer[:packet_start]
            if len(self.notification_buffer) < 4:
                return

            packet_length = self.notification_buffer[3] + PACKET_OVERHEAD
            if len(self.notification_buffer) < packet_length:
                return
            packet_data = bytes(self.notification_buffer[:packet_length])
            del self.notification_buffer[:packet_length]
            try:
                self.notification_packets.append(NiimbotPacket.from_bytes(packet_data))
            except ValueError as exception:
                self.notification_error = PrinterException(f"Invalid printer response: {exception}")
            self.notification_event.set()

    async def print_image(
        self,
        image: Image.Image,
        density: int = 3,
        quantity: int = 1,
        vertical_offset: int = 0,
        horizontal_offset: int = 0,
        timeout: float = PRINT_JOB_TIMEOUT_SECONDS,
    ) -> None:
        raster = self._prepare_raster(image, vertical_offset, horizontal_offset)
        self._validate_print_parameters(raster, density, quantity)
        try:
            await asyncio.wait_for(
                self._print_raster(raster, density, quantity),
                timeout=timeout,
            )
        except TimeoutError as exception:
            raise PrinterException(f"Print job timed out after {timeout:g} seconds") from exception

    async def _print_raster(self, raster: Image.Image, density: int, quantity: int) -> None:
        print_start_attempted = False
        end_print_attempted = False
        try:
            self._require_ack(await self.set_label_density(density), "set label density")
            self._require_ack(await self.set_label_type(1), "set label type")
            print_start_attempted = True
            self._require_ack(await self.start_print(), "start print")
            self._require_ack(await self.start_page_print(), "start page print")
            self._require_ack(await self.set_dimension(raster.height, raster.width), "set dimensions")
            self._require_ack(await self.set_quantity(quantity), "set quantity")

            for packet in self._encode_raster(raster):
                await self.write_raw(packet)
                await asyncio.sleep(0.01)

            while not await self.end_page_print():
                await asyncio.sleep(PRINT_POLL_INTERVAL_SECONDS)

            while True:
                status = await self.get_print_status()
                if status["page"] >= quantity:
                    break
                await asyncio.sleep(PRINT_POLL_INTERVAL_SECONDS)

            end_print_attempted = True
            self._require_ack(await self.end_print(), "end print")
        finally:
            if print_start_attempted and not end_print_attempted:
                try:
                    await asyncio.wait_for(self.end_print(), PRINT_CLEANUP_TIMEOUT_SECONDS)
                except Exception as exception:
                    logger.warning("Failed to terminate interrupted print job: {}", exception)

    @staticmethod
    def _require_ack(acknowledged: bool, operation: str) -> None:
        if not acknowledged:
            raise PrinterException(f"Printer rejected operation: {operation}")

    @staticmethod
    def _validate_print_parameters(raster: Image.Image, density: int, quantity: int) -> None:
        if not 1 <= density <= 5:
            raise ValueError("Label density must be between 1 and 5")
        if not 1 <= quantity <= MAX_PROTOCOL_VALUE:
            raise ValueError(f"Print quantity must be between 1 and {MAX_PROTOCOL_VALUE}")
        if not 1 <= raster.width <= MAX_RASTER_WIDTH:
            raise ValueError(f"Raster width must be between 1 and {MAX_RASTER_WIDTH}")
        if not 1 <= raster.height <= MAX_PROTOCOL_VALUE:
            raise ValueError(f"Raster height must be between 1 and {MAX_PROTOCOL_VALUE}")

    def _prepare_raster(
        self,
        image: Image.Image,
        vertical_offset: int = 0,
        horizontal_offset: int = 0,
    ) -> Image.Image:
        raster = ImageOps.invert(image.convert("L")).convert("1")
        if horizontal_offset > 0:
            raster = ImageOps.expand(raster, border=(horizontal_offset, 0, 0, 0), fill=0)
        elif horizontal_offset < 0:
            raster = raster.crop((-horizontal_offset, 0, raster.width, raster.height))
        if vertical_offset > 0:
            raster = ImageOps.expand(raster, border=(0, vertical_offset, 0, 0), fill=0)
        elif vertical_offset < 0:
            raster = raster.crop((0, -vertical_offset, raster.width, raster.height))
        return raster

    def _encode_image(
        self,
        image: Image.Image,
        vertical_offset: int = 0,
        horizontal_offset: int = 0,
    ):
        yield from self._encode_raster(self._prepare_raster(image, vertical_offset, horizontal_offset))

    @staticmethod
    def _encode_raster(raster: Image.Image):
        for y in range(raster.height):
            line_data = [raster.getpixel((x, y)) for x in range(raster.width)]
            line_data = "".join("0" if pix == 0 else "1" for pix in line_data)
            row_size = math.ceil(raster.width / 8)
            line_data = line_data.ljust(row_size * 8, "0")
            line_data = int(line_data, 2).to_bytes(row_size, "big")
            counts = (0, 0, 0)  # It seems like you can always send zeros
            header = struct.pack(RASTER_HEADER_FORMAT, y, *counts, 1)
            pkt = NiimbotPacket(0x85, header + line_data)
            yield pkt

    async def get_info(self, key):
        response = await self.send_command(
            RequestCodeEnum.GET_INFO,
            bytes((key,)),
            response_offset=key,
        )

        match key:
            case InfoEnum.DEVICESERIAL:
                return response.data.hex()
            case InfoEnum.SOFTVERSION:
                return packet_to_int(response) / 100
            case InfoEnum.HARDVERSION:
                return packet_to_int(response) / 100
            case _:
                return packet_to_int(response)

    async def get_rfid(self):
        packet = await self.send_command(RequestCodeEnum.GET_RFID, b"\x01")
        data = packet.data

        if data[0] == 0:
            return None
        uuid = data[0:8].hex()
        idx = 8

        barcode_len = data[idx]
        idx += 1
        barcode = data[idx : idx + barcode_len].decode()

        idx += barcode_len
        serial_len = data[idx]
        idx += 1
        serial = data[idx : idx + serial_len].decode()

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
        if not 1 <= n <= 3:
            raise ValueError("Label type must be between 1 and 3")
        packet = await self.send_command(
            RequestCodeEnum.SET_LABEL_TYPE,
            bytes((n,)),
            response_offset=16,
        )
        return bool(packet.data[0])

    async def set_label_density(self, n):
        if not 1 <= n <= 5:
            raise ValueError("Label density must be between 1 and 5")
        packet = await self.send_command(
            RequestCodeEnum.SET_LABEL_DENSITY,
            bytes((n,)),
            response_offset=16,
        )
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
        packet = await self.send_command(
            RequestCodeEnum.ALLOW_PRINT_CLEAR,
            b"\x01",
            response_offset=16,
        )
        return bool(packet.data[0])

    async def set_dimension(self, w, h):
        if not 1 <= w <= MAX_PROTOCOL_VALUE or not 1 <= h <= MAX_PROTOCOL_VALUE:
            raise ValueError(f"Dimensions must be between 1 and {MAX_PROTOCOL_VALUE}")
        packet = await self.send_command(RequestCodeEnum.SET_DIMENSION, struct.pack(">HH", w, h))
        return bool(packet.data[0])

    async def set_quantity(self, n):
        if not 1 <= n <= MAX_PROTOCOL_VALUE:
            raise ValueError(f"Print quantity must be between 1 and {MAX_PROTOCOL_VALUE}")
        packet = await self.send_command(RequestCodeEnum.SET_QUANTITY, struct.pack(">H", n))
        return bool(packet.data[0])

    async def get_print_status(self):
        packet = await self.send_command(
            RequestCodeEnum.GET_PRINT_STATUS,
            b"\x01",
            response_offset=16,
        )
        page, progress1, progress2 = struct.unpack(">HBB", packet.data[:4])
        return {"page": page, "progress1": progress1, "progress2": progress2}
