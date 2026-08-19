import asyncio
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest
from bleak.exc import BleakError

from niimstudio.nimmy import bluetooth
from niimstudio.nimmy.exception import BLEException


def test_find_device_matches_prefix_case_insensitively(monkeypatch):
    devices = [
        SimpleNamespace(name=None, address="00"),
        SimpleNamespace(name="Other", address="11"),
        SimpleNamespace(name="D11-Printer", address="22"),
    ]

    async def fake_discover(timeout):
        assert timeout == bluetooth.BLE_SCAN_TIMEOUT_SECONDS
        return devices

    monkeypatch.setattr(bluetooth.BleakScanner, "discover", fake_discover)

    result = asyncio.run(bluetooth.find_device("d11"))

    assert result is devices[2]


def test_find_device_does_not_confuse_overlapping_model_names(monkeypatch):
    devices = [
        SimpleNamespace(name="D110-Printer", address="11"),
        SimpleNamespace(name="D11_H-Printer", address="22"),
        SimpleNamespace(name="D11-Printer", address="33"),
    ]

    async def fake_discover(timeout):
        assert timeout == bluetooth.BLE_SCAN_TIMEOUT_SECONDS
        return devices

    monkeypatch.setattr(bluetooth.BleakScanner, "discover", fake_discover)

    result = asyncio.run(bluetooth.find_device("d11"))

    assert result is devices[2]


def test_find_device_rejects_ambiguous_matches(monkeypatch):
    async def fake_discover(timeout):
        assert timeout == bluetooth.BLE_SCAN_TIMEOUT_SECONDS
        return [
            SimpleNamespace(name="D11-First", address="11"),
            SimpleNamespace(name="D11-Second", address="22"),
        ]

    monkeypatch.setattr(bluetooth.BleakScanner, "discover", fake_discover)

    with pytest.raises(BLEException, match="Multiple D11 printers found"):
        asyncio.run(bluetooth.find_device("d11"))


def test_find_device_raises_when_no_printer_matches(monkeypatch):
    async def fake_discover(timeout):
        assert timeout == bluetooth.BLE_SCAN_TIMEOUT_SECONDS
        return [SimpleNamespace(name="B21", address="11")]

    monkeypatch.setattr(bluetooth.BleakScanner, "discover", fake_discover)

    with pytest.raises(BLEException, match="Failed to find device D11"):
        asyncio.run(bluetooth.find_device("D11"))


def test_find_device_translates_scanner_failure(monkeypatch):
    async def fake_discover(timeout):
        assert timeout == bluetooth.BLE_SCAN_TIMEOUT_SECONDS
        raise BleakError("adapter unavailable")

    monkeypatch.setattr(bluetooth.BleakScanner, "discover", fake_discover)

    with pytest.raises(BLEException, match="scan failed") as error:
        asyncio.run(bluetooth.find_device("D11"))

    assert isinstance(error.value.__cause__, BleakError)


def test_scan_devices_lists_and_filters_devices(monkeypatch, capsys):
    devices = [
        SimpleNamespace(name="D11-First", address="11"),
        SimpleNamespace(name="B21-Second", address="22"),
    ]

    async def fake_discover(timeout):
        assert timeout == bluetooth.BLE_SCAN_TIMEOUT_SECONDS
        return devices

    monkeypatch.setattr(bluetooth.BleakScanner, "discover", fake_discover)

    assert asyncio.run(bluetooth.scan_devices("b21")) is devices[1]
    assert asyncio.run(bluetooth.scan_devices()) is None
    output = capsys.readouterr().out
    assert "B21-Second" in output
    assert "D11-First" in output


def test_ble_transport_lifecycle(monkeypatch):
    clients = []

    class FakeBleakClient:
        def __init__(self, address):
            self.address = address
            self.is_connected = False
            self.calls = []
            clients.append(self)

        async def connect(self):
            self.calls.append(("connect",))
            self.is_connected = True
            return None

        async def disconnect(self):
            self.calls.append(("disconnect",))
            self.is_connected = False

        async def write_gatt_char(self, char_uuid, data):
            self.calls.append(("write", char_uuid, data))

        async def start_notify(self, char_uuid, handler):
            self.calls.append(("start_notify", char_uuid, handler))

        async def stop_notify(self, char_uuid):
            self.calls.append(("stop_notify", char_uuid))

    async def exercise_transport():
        transport = bluetooth.BLETransport()
        assert await transport.connect("AA:BB") is True
        assert await transport.connect("AA:BB") is True
        handler = object()
        await transport.write(b"data", "char")
        await transport.start_notification("char", handler)
        await transport.stop_notification("char")
        await transport.disconnect()
        return handler

    monkeypatch.setattr(bluetooth, "BleakClient", FakeBleakClient)

    handler = asyncio.run(exercise_transport())

    assert clients[0].calls == [
        ("connect",),
        ("write", "char", b"data"),
        ("start_notify", "char", handler),
        ("stop_notify", "char"),
        ("disconnect",),
    ]


def test_ble_transport_context_manager_connects_and_disconnects(monkeypatch):
    clients = []

    class FakeBleakClient:
        def __init__(self, address):
            self.is_connected = False
            clients.append(self)

        async def connect(self):
            self.is_connected = True

        async def disconnect(self):
            self.is_connected = False

    async def exercise_transport():
        async with bluetooth.BLETransport("AA:BB") as transport:
            assert transport.client.is_connected is True

    monkeypatch.setattr(bluetooth, "BleakClient", FakeBleakClient)

    asyncio.run(exercise_transport())

    assert clients[0].is_connected is False


def test_ble_transport_context_manager_preserves_body_failure():
    transport = bluetooth.BLETransport()
    transport.disconnect = AsyncMock(side_effect=BLEException("disconnect failed"))

    async def exercise_transport():
        async with transport:
            raise RuntimeError("operation failed")

    with pytest.raises(RuntimeError, match="operation failed"):
        asyncio.run(exercise_transport())


def test_ble_transport_bounds_backend_operations(monkeypatch):
    class FakeBleakClient:
        def __init__(self, address):
            self.is_connected = False

        async def connect(self):
            self.is_connected = True

    observed_timeouts = []

    async def fake_wait_for(awaitable, timeout):
        observed_timeouts.append(timeout)
        awaitable.close()
        raise TimeoutError

    monkeypatch.setattr(bluetooth, "BleakClient", FakeBleakClient)
    monkeypatch.setattr(bluetooth.asyncio, "wait_for", fake_wait_for)

    with pytest.raises(BLEException, match="Failed to connect") as error:
        asyncio.run(bluetooth.BLETransport().connect("AA:BB"))

    assert isinstance(error.value.__cause__, TimeoutError)
    assert observed_timeouts == [bluetooth.BLE_OPERATION_TIMEOUT_SECONDS]


@pytest.mark.parametrize("operation", ["connect", "disconnect", "write", "start_notification", "stop_notification"])
def test_ble_transport_translates_backend_failures(operation, monkeypatch):
    class FailingBleakClient:
        def __init__(self, address):
            self.is_connected = operation != "connect"

        async def connect(self):
            raise BleakError("connect failed")

        async def disconnect(self):
            raise BleakError("disconnect failed")

        async def write_gatt_char(self, char_uuid, data):
            raise BleakError("write failed")

        async def start_notify(self, char_uuid, handler):
            raise BleakError("notify failed")

        async def stop_notify(self, char_uuid):
            raise BleakError("notify failed")

    async def invoke_operation():
        transport = bluetooth.BLETransport()
        transport.client = FailingBleakClient("AA:BB")
        if operation == "connect":
            await transport.connect("AA:BB")
        elif operation == "disconnect":
            await transport.disconnect()
        elif operation == "write":
            await transport.write(b"data", "char")
        elif operation == "start_notification":
            await transport.start_notification("char", object())
        else:
            await transport.stop_notification("char")

    monkeypatch.setattr(bluetooth, "BleakClient", FailingBleakClient)

    with pytest.raises(BLEException):
        asyncio.run(invoke_operation())


@pytest.mark.parametrize("operation", ["write", "start_notification", "stop_notification"])
def test_ble_transport_rejects_operations_while_disconnected(operation):
    transport = bluetooth.BLETransport()

    async def invoke_operation():
        if operation == "write":
            await transport.write(b"data", "char")
        elif operation == "start_notification":
            await transport.start_notification("char", object())
        else:
            await transport.stop_notification("char")

    with pytest.raises(BLEException, match="not connected"):
        asyncio.run(invoke_operation())
