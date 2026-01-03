from homeassistant.helpers import entity_platform
from .const import DOMAIN
from .sensor import SmartScaleSensor
from .ble_handler import SmartScaleBLE
import asyncio

async def async_setup_entry(hass, entry):
    ble_address = entry.data["ble_address"]
    device_name = entry.data.get("device_name", "SmartScale")

    ble = SmartScaleBLE(ble_address, device_name)

    sensors = [
        SmartScaleSensor("Smart Scale Weight", "weight"),
        SmartScaleSensor("Smart Scale Body", "body"),
        SmartScaleSensor("Smart Scale Person", "person")
    ]

    def update_ha(sensor_type, data):
        for sensor in sensors:
            if sensor._type == sensor_type:
                sensor.update_data(data)
                sensor.async_write_ha_state()

    ble.register_callback(update_ha)

    async def poll_scale():
        while True:
            try:
                await ble.connect_and_read()
            except Exception as e:
                hass.logger.error(f"BLE error: {e}")
            await asyncio.sleep(30)

    hass.async_create_task(poll_scale())

    hass.helpers.discovery.load_platform("sensor", DOMAIN, {}, entry.data)
    return True
