import asyncio
import struct
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from PIL import Image

from niimstudio.nimmy.exception import BLEException, PrinterException
from niimstudio.nimmy.packet import NiimbotPacket
from niimstudio.nimmy.printer import MAX_RASTER_WIDTH, InfoEnum, PrinterClient, RequestCodeEnum


def create_printer():
    return PrinterClient(SimpleNamespace(name="D11", address="AA:BB"))


def test_connect_discovers_supported_characteristic_and_disconnects():
    printer = create_printer()
    supported_characteristic = SimpleNamespace(
        uuid="supported",
        handle=1,
        properties=["read", "write-without-response", "notify"],
    )
    ignored_characteristic = SimpleNamespace(uuid="ignored", handle=2, properties=["read"])
    printer.transport = SimpleNamespace(
        client=SimpleNamespace(
            services=[
                SimpleNamespace(uuid="ignored-service", characteristics=[ignored_characteristic]),
                SimpleNamespace(
                    uuid="printer-service",
                    characteristics=[supported_characteristic, ignored_characteristic],
                ),
            ]
        ),
        connect=AsyncMock(return_value=True),
        disconnect=AsyncMock(),
    )

    assert asyncio.run(printer.connect()) is True
    asyncio.run(printer.disconnect())

    assert printer.char_uuid == "supported"
    printer.transport.connect.assert_awaited_once_with("AA:BB")
    printer.transport.disconnect.assert_awaited_once_with()


def test_find_characteristics_rejects_unsupported_services():
    printer = create_printer()
    printer.transport.client = SimpleNamespace(
        services=[
            SimpleNamespace(
                uuid="service",
                characteristics=[SimpleNamespace(uuid="char", handle=1, properties=["read"])],
            )
        ]
    )

    with pytest.raises(PrinterException, match="Cannot find bluetooth characteristics"):
        asyncio.run(printer.find_characteristics())


def test_find_characteristics_rejects_ambiguous_candidates():
    printer = create_printer()
    properties = ["read", "write-without-response", "notify"]
    printer.transport.client = SimpleNamespace(
        services=[
            SimpleNamespace(
                uuid="service",
                characteristics=[
                    SimpleNamespace(uuid="first", properties=properties),
                    SimpleNamespace(uuid="second", properties=properties),
                ],
            )
        ]
    )

    with pytest.raises(PrinterException, match="Cannot find bluetooth characteristics"):
        asyncio.run(printer.find_characteristics())


def test_send_command_writes_packet_reads_response_and_cleans_up():
    printer = create_printer()

    class FakeTransport:
        def __init__(self):
            self.client = SimpleNamespace(is_connected=True)
            self.handler = None
            self.written = []
            self.stopped = []

        async def start_notification(self, char_uuid, handler):
            self.handler = handler

        async def write(self, data, char_uuid):
            self.written.append((char_uuid, data))
            self.handler(None, NiimbotPacket(0x41, b"\x01\x02").to_bytes())

        async def stop_notification(self, char_uuid):
            self.stopped.append(char_uuid)

    transport = FakeTransport()
    printer.transport = transport
    printer.char_uuid = "char"

    response = asyncio.run(printer.send_command(RequestCodeEnum.GET_INFO, bytes((InfoEnum.SOFTVERSION,))))

    request = NiimbotPacket.from_bytes(transport.written[0][1])
    assert request.type == RequestCodeEnum.GET_INFO
    assert request.data == bytes((InfoEnum.SOFTVERSION,))
    assert response.type == 0x41
    assert response.data == b"\x01\x02"
    assert transport.stopped == ["char"]
    assert printer.notification_event.is_set() is False


def test_send_command_times_out_and_stops_notifications():
    printer = create_printer()

    class FakeTransport:
        def __init__(self):
            self.client = SimpleNamespace(is_connected=True)
            self.stopped = []

        async def start_notification(self, char_uuid, handler):
            pass

        async def write(self, data, char_uuid):
            pass

        async def stop_notification(self, char_uuid):
            self.stopped.append(char_uuid)

    transport = FakeTransport()
    printer.transport = transport
    printer.char_uuid = "char"

    with pytest.raises(PrinterException, match="GET_INFO timed out"):
        asyncio.run(printer.send_command(RequestCodeEnum.GET_INFO, b"\x01", timeout=0.001))

    assert transport.stopped == ["char"]


def test_send_command_accepts_fragmented_response():
    printer = create_printer()
    response_bytes = NiimbotPacket(0x41, b"\x01\x02").to_bytes()

    class FakeTransport:
        def __init__(self):
            self.client = SimpleNamespace(is_connected=True)
            self.handler = None

        async def start_notification(self, char_uuid, handler):
            self.handler = handler

        async def write(self, data, char_uuid):
            self.handler(None, response_bytes[:3])
            self.handler(None, response_bytes[3:6])
            self.handler(None, response_bytes[6:])

        async def stop_notification(self, char_uuid):
            pass

    printer.transport = FakeTransport()
    printer.char_uuid = "char"

    response = asyncio.run(printer.send_command(RequestCodeEnum.GET_INFO, b"\x01"))

    assert response.type == 0x41
    assert response.data == b"\x01\x02"


def test_send_command_ignores_unrelated_response():
    printer = create_printer()
    unrelated = NiimbotPacket(0x99, b"unrelated").to_bytes()
    expected = NiimbotPacket(0x41, b"expected").to_bytes()

    class FakeTransport:
        def __init__(self):
            self.client = SimpleNamespace(is_connected=True)
            self.handler = None

        async def start_notification(self, char_uuid, handler):
            self.handler = handler

        async def write(self, data, char_uuid):
            self.handler(None, unrelated + expected)

        async def stop_notification(self, char_uuid):
            pass

    printer.transport = FakeTransport()
    printer.char_uuid = "char"

    response = asyncio.run(printer.send_command(RequestCodeEnum.GET_INFO, b"\x01"))

    assert response.type == 0x41
    assert response.data == b"expected"


def test_send_command_reports_malformed_response():
    printer = create_printer()
    malformed = bytearray(NiimbotPacket(0x41, b"\x01").to_bytes())
    malformed[-3] ^= 0xFF

    class FakeTransport:
        def __init__(self):
            self.client = SimpleNamespace(is_connected=True)
            self.handler = None

        async def start_notification(self, char_uuid, handler):
            self.handler = handler

        async def write(self, data, char_uuid):
            self.handler(None, malformed)

        async def stop_notification(self, char_uuid):
            pass

    printer.transport = FakeTransport()
    printer.char_uuid = "char"

    with pytest.raises(PrinterException, match="Invalid printer response"):
        asyncio.run(printer.send_command(RequestCodeEnum.GET_INFO, b"\x01"))


def test_send_command_reports_unsupported_response():
    printer = create_printer()

    class FakeTransport:
        def __init__(self):
            self.client = SimpleNamespace(is_connected=True)
            self.handler = None

        async def start_notification(self, char_uuid, handler):
            self.handler = handler

        async def write(self, data, char_uuid):
            self.handler(None, NiimbotPacket(0x00, b"").to_bytes())

        async def stop_notification(self, char_uuid):
            pass

    printer.transport = FakeTransport()
    printer.char_uuid = "char"

    with pytest.raises(PrinterException, match="does not support"):
        asyncio.run(printer.send_command(RequestCodeEnum.GET_INFO, b"\x01"))


def test_send_command_translates_ble_failure():
    printer = create_printer()

    class FakeTransport:
        def __init__(self):
            self.client = SimpleNamespace(is_connected=True)

        async def start_notification(self, char_uuid, handler):
            raise BLEException("adapter failed")

    printer.transport = FakeTransport()
    printer.char_uuid = "char"

    with pytest.raises(PrinterException, match="Bluetooth communication failed") as error:
        asyncio.run(printer.send_command(RequestCodeEnum.GET_INFO, b"\x01"))

    assert isinstance(error.value.__cause__, BLEException)


@pytest.mark.parametrize(
    ("color", "horizontal_offset", "vertical_offset", "expected_rows"),
    [
        (1, 0, 0, [(0, b"\x00")]),
        (0, 0, 0, [(0, b"\xff")]),
        (1, 8, 0, [(0, b"\x00\x00")]),
        (1, -4, 0, [(0, b"\x00")]),
        (1, 0, 1, [(0, b"\x00"), (1, b"\x00")]),
        (1, 0, -1, []),
    ],
)
def test_encode_image_applies_monochrome_and_offsets(
    color,
    horizontal_offset,
    vertical_offset,
    expected_rows,
):
    printer = create_printer()
    image = Image.new("1", (8, 1), color=color)

    packets = list(printer._encode_image(image, vertical_offset, horizontal_offset))
    rows = [(struct.unpack(">H3BB", packet.data[:6])[0], packet.data[6:]) for packet in packets]

    assert all(packet.type == 0x85 for packet in packets)
    assert rows == expected_rows


@pytest.mark.parametrize(
    ("width", "expected"),
    [
        (1, b"\x80"),
        (7, b"\xfe"),
        (9, b"\xff\x80"),
        (15, b"\xff\xfe"),
    ],
)
def test_encode_image_right_pads_non_byte_aligned_rows(width, expected):
    printer = create_printer()

    packet = next(printer._encode_image(Image.new("1", (width, 1), color=0)))

    assert packet.data[6:] == expected


def test_print_image_rejects_rows_larger_than_packet_payload():
    printer = create_printer()

    with pytest.raises(ValueError, match=rf"between 1 and {MAX_RASTER_WIDTH}"):
        asyncio.run(printer.print_image(Image.new("1", (MAX_RASTER_WIDTH + 1, 1))))


def test_encode_image_accepts_largest_packet_row():
    printer = create_printer()

    packet = next(printer._encode_image(Image.new("1", (MAX_RASTER_WIDTH, 1))))

    assert len(packet.data) == 255


def test_print_image_runs_complete_protocol_sequence(monkeypatch):
    printer = create_printer()
    printer.set_label_density = AsyncMock(return_value=True)
    printer.set_label_type = AsyncMock(return_value=True)
    printer.start_print = AsyncMock(return_value=True)
    printer.start_page_print = AsyncMock(return_value=True)
    printer.set_dimension = AsyncMock(return_value=True)
    printer.set_quantity = AsyncMock(return_value=True)
    printer.write_raw = AsyncMock()
    printer.end_page_print = AsyncMock(side_effect=[False, True])
    printer.get_print_status = AsyncMock(
        side_effect=[
            {"page": 1, "progress1": 50, "progress2": 50},
            {"page": 2, "progress1": 100, "progress2": 100},
        ]
    )
    printer.end_print = AsyncMock(return_value=True)
    packets = [NiimbotPacket(0x85, b"first"), NiimbotPacket(0x85, b"second")]
    raster = Image.new("1", (20, 11))
    monkeypatch.setattr(printer, "_prepare_raster", lambda *args: raster)
    monkeypatch.setattr(printer, "_encode_raster", lambda *args: iter(packets))
    monkeypatch.setattr("niimstudio.nimmy.printer.asyncio.sleep", AsyncMock())
    image = Image.new("1", (16, 8))

    asyncio.run(
        printer.print_image(
            image,
            density=2,
            quantity=2,
            vertical_offset=3,
            horizontal_offset=4,
        )
    )

    printer.set_label_density.assert_awaited_once_with(2)
    printer.set_label_type.assert_awaited_once_with(1)
    printer.start_print.assert_awaited_once_with()
    printer.start_page_print.assert_awaited_once_with()
    printer.set_dimension.assert_awaited_once_with(11, 20)
    printer.set_quantity.assert_awaited_once_with(2)
    assert [call.args[0] for call in printer.write_raw.await_args_list] == packets
    assert printer.end_page_print.await_count == 2
    assert printer.get_print_status.await_count == 2
    printer.end_print.assert_awaited_once_with()


def test_print_image_rejects_failed_acknowledgement_before_sending_rows():
    printer = create_printer()
    printer.set_label_density = AsyncMock(return_value=False)
    printer.set_label_type = AsyncMock(return_value=True)
    printer.start_print = AsyncMock(return_value=True)
    printer.write_raw = AsyncMock()
    printer.end_print = AsyncMock(return_value=True)

    with pytest.raises(PrinterException, match="set label density"):
        asyncio.run(printer.print_image(Image.new("1", (8, 1))))

    printer.start_print.assert_not_awaited()
    printer.write_raw.assert_not_awaited()
    printer.end_print.assert_not_awaited()


def test_print_image_times_out_and_terminates_started_job(monkeypatch):
    printer = create_printer()
    printer.set_label_density = AsyncMock(return_value=True)
    printer.set_label_type = AsyncMock(return_value=True)
    printer.start_print = AsyncMock(return_value=True)
    printer.start_page_print = AsyncMock(return_value=True)
    printer.set_dimension = AsyncMock(return_value=True)
    printer.set_quantity = AsyncMock(return_value=True)
    printer.write_raw = AsyncMock()
    printer.end_page_print = AsyncMock(return_value=False)
    printer.end_print = AsyncMock(return_value=True)
    monkeypatch.setattr("niimstudio.nimmy.printer.PRINT_POLL_INTERVAL_SECONDS", 0.01)

    with pytest.raises(PrinterException, match="timed out"):
        asyncio.run(printer.print_image(Image.new("1", (8, 1)), timeout=0.001))

    printer.end_print.assert_awaited_once_with()


def test_print_image_terminates_job_when_start_response_fails():
    printer = create_printer()
    printer.set_label_density = AsyncMock(return_value=True)
    printer.set_label_type = AsyncMock(return_value=True)
    printer.start_print = AsyncMock(side_effect=PrinterException("start response lost"))
    printer.end_print = AsyncMock(return_value=True)

    with pytest.raises(PrinterException, match="start response lost"):
        asyncio.run(printer.print_image(Image.new("1", (8, 1))))

    printer.end_print.assert_awaited_once_with()


@pytest.mark.parametrize(
    ("key", "data", "expected"),
    [
        (InfoEnum.DEVICESERIAL, b"\x01\x02", "0102"),
        (InfoEnum.SOFTVERSION, b"\x00\x7b", 1.23),
        (InfoEnum.HARDVERSION, b"\x01\xc8", 4.56),
        (InfoEnum.BATTERY, b"\x64", 100),
    ],
)
def test_get_info_decodes_values(key, data, expected):
    printer = create_printer()
    printer.send_command = AsyncMock(return_value=NiimbotPacket(0x41, data))

    result = asyncio.run(printer.get_info(key))

    assert result == expected
    printer.send_command.assert_awaited_once_with(
        RequestCodeEnum.GET_INFO,
        bytes((key,)),
        response_offset=key,
    )


@pytest.mark.parametrize(
    ("method_name", "argument", "request_code", "data", "response_offset", "response_data"),
    [
        ("set_label_type", 2, RequestCodeEnum.SET_LABEL_TYPE, b"\x02", 16, b"\x01"),
        ("set_label_density", 4, RequestCodeEnum.SET_LABEL_DENSITY, b"\x04", 16, b"\x01"),
        ("allow_print_clear", None, RequestCodeEnum.ALLOW_PRINT_CLEAR, b"\x01", 16, b"\x01"),
        ("get_print_status", None, RequestCodeEnum.GET_PRINT_STATUS, b"\x01", 16, b"\x00\x01\x02\x03"),
    ],
)
def test_commands_use_protocol_response_offsets(
    method_name,
    argument,
    request_code,
    data,
    response_offset,
    response_data,
):
    printer = create_printer()
    printer.send_command = AsyncMock(return_value=NiimbotPacket(0x00, response_data))

    method = getattr(printer, method_name)
    asyncio.run(method() if argument is None else method(argument))

    printer.send_command.assert_awaited_once_with(
        request_code,
        data,
        response_offset=response_offset,
    )


@pytest.mark.parametrize(
    ("data", "expected"),
    [
        (
            bytes(range(13)),
            {"closing_state": 9, "power_level": 10, "paper_state": 11, "rfid_read_state": 12},
        ),
        (
            bytes(range(20)),
            {"closing_state": None, "power_level": None, "paper_state": 18, "rfid_read_state": 19},
        ),
        (
            bytes(range(9)),
            {"closing_state": 8, "power_level": None, "paper_state": None, "rfid_read_state": None},
        ),
    ],
)
def test_heartbeat_decodes_supported_responses(data, expected):
    printer = create_printer()
    printer.send_command = AsyncMock(return_value=NiimbotPacket(0xDD, data))

    result = asyncio.run(printer.heartbeat())

    assert result == expected


def test_get_rfid_decodes_label_data():
    printer = create_printer()
    data = (
        bytes.fromhex("0102030405060708")
        + bytes((3,))
        + b"ABC"
        + bytes((3,))
        + b"XYZ"
        + struct.pack(">HHB", 100, 25, 2)
    )
    printer.send_command = AsyncMock(return_value=NiimbotPacket(0x1B, data))

    result = asyncio.run(printer.get_rfid())

    assert result == {
        "uuid": "0102030405060708",
        "barcode": "ABC",
        "serial": "XYZ",
        "used_len": 25,
        "total_len": 100,
        "type": 2,
    }


def test_get_rfid_returns_none_for_missing_label():
    printer = create_printer()
    printer.send_command = AsyncMock(return_value=NiimbotPacket(0x1B, b"\x00"))

    assert asyncio.run(printer.get_rfid()) is None


@pytest.mark.parametrize(
    ("method_name", "value", "message"),
    [
        ("set_label_type", 0, "between 1 and 3"),
        ("set_label_type", 4, "between 1 and 3"),
        ("set_label_density", 0, "between 1 and 5"),
        ("set_label_density", 6, "between 1 and 5"),
        ("set_quantity", 0, "between 1 and 65535"),
        ("set_quantity", 65536, "between 1 and 65535"),
    ],
)
def test_printer_rejects_invalid_settings(method_name, value, message):
    printer = create_printer()

    with pytest.raises(ValueError, match=message):
        asyncio.run(getattr(printer, method_name)(value))
