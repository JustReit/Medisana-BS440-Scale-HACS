import voluptuous as vol
from homeassistant import config_entries
from .const import DOMAIN, CONF_BLE_ADDRESS, CONF_DEVICE_NAME, CONF_DEVICE_MODEL

class SmartScaleConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            return self.async_create_entry(title="Smart Scale", data=user_input)

        data_schema = vol.Schema({
            vol.Required(CONF_BLE_ADDRESS): str,
            vol.Optional(CONF_DEVICE_NAME, default="SmartScale"): str,
            vol.Optional(CONF_DEVICE_MODEL, default="BS440"): str
        })
        return self.async_show_form(step_id="user", data_schema=data_schema)
