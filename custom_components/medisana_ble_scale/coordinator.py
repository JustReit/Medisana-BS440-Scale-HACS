import asyncio
import logging
import time
import os
from struct import unpack
from datetime import timedelta

from bleak_retry_connector import BleakClientWithServiceCache, establish_connection
from homeassistant.components import bluetooth
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers.storage import Store
from .const import (
    DOMAIN, CONF_MAC, CHAR_PERSON, CHAR_WEIGHT, CHAR_BODY, CHAR_COMMAND, TIME_OFFSET, CONF_USERS
)


_LOGGER = logging.getLogger(__name__)

class BS440Coordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        self.mac = entry.data[CONF_MAC].upper()
        self.user_names = {}
        user_str = entry.data.get(CONF_USERS, "")
        if user_str:
            for item in user_str.split(","):
                if ":" in item:
                    k, v = item.split(":", 1)
                    self.user_names[int(k.strip())] = v.strip()

        self._store = Store(hass, 1, f"{DOMAIN}_{self.mac}")
        super().__init__(
            hass, _LOGGER, name=DOMAIN,
            update_interval=timedelta(seconds=30)
        )
        self.data = {}
        self._temp_person = None
        self._temp_weight = None
        self._temp_body = None
        self._data_received_event = asyncio.Event()

    async def async_load_data(self):
        """Load stored data from disk."""
        stored_data = await self._store.async_load()
        if stored_data:
            # Convert keys back to int because JSON stores keys as strings
            self.data = {int(k): v for k, v in stored_data.items()}
            _LOGGER.debug("Loaded persisted data for %s: %s", self.mac, self.data)

    def _decode_person(self, values):
        data = unpack('BxBxBBBxB', bytes(values[0:9]))
        return {"person": data[1], "size": data[4]}

    def _decode_weight(self, values):
        data = unpack('<BHxxIxxxxB', bytes(values[0:14]))
        return {"weight": data[1] / 100.0, "person": data[3]}

    def _decode_body(self, values):
        data = unpack('<BIBHHHHH', bytes(values[0:16]))
        return {
            "person": data[2],
            "kcal": data[3],
            "fat": (0x0fff & data[4]) / 10.0,
            "tbw": (0x0fff & data[5]) / 10.0,
            "muscle": (0x0fff & data[6]) / 10.0,
            "bone": (0x0fff & data[7]) / 10.0
        }

    def _notification_handler(self, sender, data):
        sender_str = str(sender).lower()
        _LOGGER.debug("BLE Notification from %s: %s", sender_str, data.hex())

        if CHAR_PERSON.lower() in sender_str:
            self._temp_person = self._decode_person(data)
        elif CHAR_WEIGHT.lower() in sender_str:
            self._temp_weight = self._decode_weight(data)
        elif CHAR_BODY.lower() in sender_str:
            self._temp_body = self._decode_body(data)

        if self._temp_weight:
            if self._temp_weight["person"] == 255:
                self._data_received_event.set()
            elif self._temp_person and self._temp_body:
                self._data_received_event.set()

    async def _async_update_data(self):
        ble_device = bluetooth.async_ble_device_from_address(self.hass, self.mac, connectable=True)
        if not ble_device:
            _LOGGER.debug("Scale %s not found in range", self.mac)
            return self.data

        self._temp_person = self._temp_weight = self._temp_body = None
        self._data_received_event.clear()

        try:
            client = await establish_connection(BleakClientWithServiceCache, ble_device, self.mac)
            async with client:
                _LOGGER.debug("Connected to %s via Proxy", self.mac)
                await client.start_notify(CHAR_PERSON, self._notification_handler)
                await client.start_notify(CHAR_WEIGHT, self._notification_handler)
                await client.start_notify(CHAR_BODY, self._notification_handler)

                timestamp = int(time.time() - TIME_OFFSET)
                cmd = bytearray([0x02]) + timestamp.to_bytes(4, "little")
                await client.write_gatt_char(CHAR_COMMAND, cmd)

                try:
                    await asyncio.wait_for(self._data_received_event.wait(), timeout=15)
                except asyncio.TimeoutError:
                    _LOGGER.debug("Timeout waiting for specific user data packets")

                if self._temp_weight:
                    pid = self._temp_weight["person"]
                    user_data = {
                        "weight": self._temp_weight["weight"],
                        "person": pid,
                        "last_measurement": time.time() # Add timestamp here
                    }
                    
                    if pid != 255 and self._temp_body and self._temp_person:
                        user_data.update({
                            "fat": self._temp_body["fat"],
                            "tbw": self._temp_body["tbw"],
                            "muscle": self._temp_body["muscle"],
                            "bone": self._temp_body["bone"],
                            "kcal": self._temp_body["kcal"],
                        })
                        size_m = self._temp_person["size"] / 100.0
                        user_data["bmi"] = round(user_data["weight"] / (size_m**2), 1) if size_m > 0 else None

                    self.data[pid] = user_data
                    _LOGGER.info("Updated data for Person %s", pid)
                    await self._store.async_save(self.data)

        except Exception as e:
            _LOGGER.error("BLE Error: %s", e)
        
        return self.data