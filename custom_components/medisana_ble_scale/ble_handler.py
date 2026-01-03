import asyncio
from bleak import BleakScanner, BleakClient
from .const import CHAR_PERSON, CHAR_WEIGHT, CHAR_BODY, CHAR_COMMAND, TIME_OFFSET
import logging
from struct import unpack

_LOGGER = logging.getLogger(__name__)

class SmartScaleBLE:
    def __init__(self, ble_address, device_name):
        self.ble_address = ble_address
        self.device_name = device_name
        self.persondata = []
        self.weightdata = []
        self.bodydata = []

        self.callbacks = []

    def register_callback(self, callback):
        """Register callback to send updates to HA sensors."""
        self.callbacks.append(callback)

    # --------------------
    # Decoders
    # --------------------
    def decode_person(self, values):
        data = unpack('BxBxBBBxB', bytes(values[0:9]))
        return {
            "valid": data[0] == 0x84,
            "person": data[1],
            "gender": "male" if data[2] == 1 else "female",
            "age": data[3],
            "size": data[4],
            "activity": "high" if data[5] == 3 else "normal"
        }

    def decode_weight(self, values):
        data = unpack('<BHxxIxxxxB', bytes(values[0:14]))
        return {
            "valid": data[0] == 0x1d,
            "weight": data[1] / 100.0,
            "timestamp": data[2] + TIME_OFFSET,
            "person": data[3]
        }

    def decode_body(self, values):
        data = unpack('<BIBHHHHH', bytes(values[0:16]))
        return {
            "valid": data[0] == 0x6f,
            "timestamp": data[1] + TIME_OFFSET,
            "person": data[2],
            "kcal": data[3],
            "fat": (0x0fff & data[4]) / 10.0,
            "tbw": (0x0fff & data[5]) / 10.0,
            "muscle": (0x0fff & data[6]) / 10.0,
            "bone": (0x0fff & data[7]) / 10.0
        }

    # --------------------
    # BLE Notification Handlers
    # --------------------
    def handle_person(self, _, data):
        result = self.decode_person(data)
        if result not in self.persondata:
            self.persondata.append(result)
            self._notify_all("person", result)

    def handle_weight(self, _, data):
        result = self.decode_weight(data)
        if result not in self.weightdata:
            self.weightdata.append(result)
            self._notify_all("weight", result)

    def handle_body(self, _, data):
        result = self.decode_body(data)
        if result not in self.bodydata:
            self.bodydata.append(result)
            self._notify_all("body", result)

    def _notify_all(self, data_type, data):
        for cb in self.callbacks:
            cb(data_type, data)

    # --------------------
    # BLE scan/connect loop
    # --------------------
    async def connect_and_read(self):
        _LOGGER.info(f"Scanning for device {self.device_name} ({self.ble_address})")
        devices = await BleakScanner.discover()
        device = next((d for d in devices if d.address.upper() == self.ble_address.upper() or d.name == self.device_name), None)

        if not device:
            _LOGGER.warning("Scale not found")
            return

        async with BleakClient(device.address) as client:
            if not client.is_connected:
                _LOGGER.error("BLE connect failed")
                return

            _LOGGER.info("Connected to scale")
            await client.start_notify(CHAR_PERSON, self.handle_person)
            await client.start_notify(CHAR_WEIGHT, self.handle_weight)
            await client.start_notify(CHAR_BODY, self.handle_body)

            timestamp = int(time.time() - TIME_OFFSET)
            cmd = bytearray([0x02]) + timestamp.to_bytes(4, "little")
            await client.write_gatt_char(CHAR_COMMAND, cmd)
            _LOGGER.debug(f"Sent command: {cmd.hex()}")

            await asyncio.sleep(10)  # wait for notifications
