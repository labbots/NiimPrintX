import asyncio
from bleak import BleakClient, BleakScanner

from .exception import BLEException
from .logger_config import get_logger
from .models import matches_model

logger = get_logger()


async def find_device(device_name_prefix=None):
    # Bleak 1.x removed BLEDevice.metadata; use advertisement data instead.
    # Prefer the advertising address with no service UUIDs (Niimbot dual-address quirk),
    # but fall back to devices that advertise services (required for B21S).
    discovered = await BleakScanner.discover(return_adv=True)
    model = (device_name_prefix or "").lower()
    fallback = None
    for device, adv in discovered.values():
        if not matches_model(device.name, model):
            continue
        service_uuids = list(getattr(adv, "service_uuids", None) or [])
        if len(service_uuids) == 0:
            return device
        if fallback is None:
            fallback = device
    if fallback is not None:
        return fallback
    raise BLEException(f"Failed to find device {device_name_prefix}")


async def scan_devices(device_name=None):
    print("Scanning for devices...")
    devices = await BleakScanner.discover()
    for device in devices:
        if device_name:
            if device.name and matches_model(device.name, device_name):
                print(f"Found device: {device.name} at {device.address}")
                return device
        else:
            print(f"Found device: {device.name} at {device.address}")
    return None


class BLETransport:
    def __init__(self, address=None):
        self.address = address
        self.client = None

    async def __aenter__(self):
        if self.address:
            self.client = BleakClient(self.address)
            await self.client.connect()
            if self.client.is_connected:
                await self._ensure_mtu()
                logger.info(f"Connected to {self.address}")
                return self
            raise BLEException(f"Failed to connect to the BLE device at {self.address}")
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.client:
            await self.client.disconnect()
            logger.info("Disconnected.")

    async def connect(self, address):
        # Bleak 1.x connect() returns None; use is_connected for success.
        if self.client is None:
            self.client = BleakClient(address)
        if not self.client.is_connected:
            await self.client.connect()
            await self._ensure_mtu()
        return self.client.is_connected

    async def _ensure_mtu(self):
        """Raise ATT MTU so write-with-response can carry full bitmap rows (~61 bytes)."""
        if not self.client:
            return
        backend = getattr(self.client, "_backend", None)
        if backend is not None and hasattr(backend, "_acquire_mtu"):
            try:
                await backend._acquire_mtu()
                logger.info(f"BLE MTU negotiated: {getattr(self.client, 'mtu_size', '?')}")
            except Exception as e:
                logger.warning(f"BLE MTU negotiate failed: {e}")

    async def disconnect(self):
        if self.client and self.client.is_connected:
            await self.client.disconnect()

    async def write(self, data, char_uuid):
        if not (self.client and self.client.is_connected):
            raise BLEException("BLE client is not connected.")

        # BlueZ often keeps max_write_without_response_size at 20 even after MTU
        # negotiation. PrintBitmapRow packets are ~61 bytes, so we must use
        # write-with-response (uses negotiated MTU) for large payloads. Truncated
        # write-without-response packets produce blank labels on B21S.
        char = None
        try:
            char = self.client.services.get_characteristic(char_uuid)
        except Exception:
            pass

        max_wo = 20
        if char is not None:
            max_wo = getattr(char, "max_write_without_response_size", 20) or 20

        props = set(getattr(char, "properties", None) or [])
        if len(data) <= max_wo and "write-without-response" in props:
            use_response = False
        elif "write" in props:
            use_response = True
        else:
            use_response = False

        await self.client.write_gatt_char(char_uuid, data, response=use_response)

    async def start_notification(self, char_uuid, handler):
        if self.client and self.client.is_connected:
            await self.client.start_notify(char_uuid, handler)
        else:
            raise BLEException("BLE client is not connected.")

    async def stop_notification(self, char_uuid):
        if self.client and self.client.is_connected:
            await self.client.stop_notify(char_uuid)
        else:
            raise BLEException("BLE client is not connected.")
