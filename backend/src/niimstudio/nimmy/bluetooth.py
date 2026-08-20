import asyncio
import re
from collections.abc import Callable
from typing import Any

from bleak import BleakClient, BleakScanner
from bleak.exc import BleakError

from niimstudio.domain.printer_capabilities import PRINTER_CAPABILITIES

from .exception import BLEException
from .logger_config import get_logger

BLE_OPERATION_TIMEOUT_SECONDS = 10.0
BLE_SCAN_TIMEOUT_SECONDS = 10.0

logger = get_logger()


def _normalize_model(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.lower())


def _device_model(name: str) -> str | None:
    normalized_name = _normalize_model(name)
    matches = [
        (printer.model_id, prefix)
        for printer in PRINTER_CAPABILITIES
        for prefix in printer.discovery_prefixes
        if normalized_name.startswith(_normalize_model(prefix))
    ]
    match = max(matches, key=lambda candidate: len(_normalize_model(candidate[1])), default=None)
    return match[0] if match else None


async def find_device(device_name_prefix: str):
    try:
        devices = await BleakScanner.discover(timeout=BLE_SCAN_TIMEOUT_SECONDS)
    except (BleakError, OSError, TimeoutError) as exception:
        raise BLEException("Bluetooth device scan failed") from exception

    matching_devices = [
        device for device in devices if device.name and _device_model(device.name) == device_name_prefix.lower()
    ]
    if not matching_devices:
        raise BLEException(f"Failed to find device {device_name_prefix}")
    if len(matching_devices) > 1:
        names = ", ".join(device.name or device.address for device in matching_devices)
        raise BLEException(f"Multiple {device_name_prefix.upper()} printers found: {names}")
    return matching_devices[0]


async def scan_devices(device_name: str | None = None):
    print("Scanning for devices...")
    try:
        devices = await BleakScanner.discover(timeout=BLE_SCAN_TIMEOUT_SECONDS)
    except (BleakError, OSError, TimeoutError) as exception:
        raise BLEException("Bluetooth device scan failed") from exception
    for device in devices:
        if device_name:
            if device.name and device_name.lower() in device.name.lower():
                print(f"Found device: {device.name} at {device.address}")
                return device
        else:
            print(f"Found device: {device.name} at {device.address}")
    return None


class BLETransport:
    def __init__(self, address: str | None = None):
        self.address = address
        self.client: BleakClient | None = None

    async def __aenter__(self):
        if self.address and not await self.connect(self.address):
            raise BLEException(f"Failed to connect to the BLE device at {self.address}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        try:
            await self.disconnect()
        except BLEException as exception:
            if exc_type is None:
                raise
            logger.warning("Failed to disconnect BLE device after operation failure: {}", exception)

    async def connect(self, address: str) -> bool:
        try:
            if self.client is None:
                self.client = BleakClient(address)
            if not self.client.is_connected:
                await asyncio.wait_for(self.client.connect(), BLE_OPERATION_TIMEOUT_SECONDS)
            return self.client.is_connected
        except (BleakError, OSError, TimeoutError) as exception:
            raise BLEException(f"Failed to connect to BLE device at {address}") from exception

    async def disconnect(self) -> None:
        try:
            if self.client and self.client.is_connected:
                await asyncio.wait_for(self.client.disconnect(), BLE_OPERATION_TIMEOUT_SECONDS)
        except (BleakError, OSError, TimeoutError) as exception:
            raise BLEException("Failed to disconnect BLE device") from exception

    async def write(self, data: bytes, char_uuid: str) -> None:
        if not self.client or not self.client.is_connected:
            raise BLEException("BLE client is not connected.")
        try:
            await asyncio.wait_for(
                self.client.write_gatt_char(char_uuid, data),
                BLE_OPERATION_TIMEOUT_SECONDS,
            )
        except (BleakError, OSError, TimeoutError) as exception:
            raise BLEException("Failed to write to BLE device") from exception

    async def start_notification(
        self,
        char_uuid: str,
        handler: Callable[[Any, bytearray], None],
    ) -> None:
        if not self.client or not self.client.is_connected:
            raise BLEException("BLE client is not connected.")
        try:
            await asyncio.wait_for(
                self.client.start_notify(char_uuid, handler),
                BLE_OPERATION_TIMEOUT_SECONDS,
            )
        except (BleakError, OSError, TimeoutError) as exception:
            raise BLEException("Failed to start BLE notifications") from exception

    async def stop_notification(self, char_uuid: str) -> None:
        if not self.client or not self.client.is_connected:
            raise BLEException("BLE client is not connected.")
        try:
            await asyncio.wait_for(
                self.client.stop_notify(char_uuid),
                BLE_OPERATION_TIMEOUT_SECONDS,
            )
        except (BleakError, OSError, TimeoutError) as exception:
            raise BLEException("Failed to stop BLE notifications") from exception
