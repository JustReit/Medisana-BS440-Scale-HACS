"""Config flow for BS440 BLE integration."""
import voluptuous as vol
import logging
from homeassistant import config_entries
from homeassistant.components.bluetooth import async_scanner_count
from homeassistant.helpers import config_validation as cv
from .const import DOMAIN, CONF_MAC, DEFAULT_NAME

_LOGGER = logging.getLogger(__name__)

class BS440ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BS440 BLE."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            mac = user_input[CONF_MAC].upper()
            await self.async_set_unique_id(mac)
            self._abort_if_unique_id_configured()

            # Verify if bluetooth stack is active
            if async_scanner_count(self.hass) == 0:
                errors["base"] = "no_bluetooth_adapter"
            else:
                return self.async_create_entry(
                    title=f"{DEFAULT_NAME} ({mac})",
                    data={CONF_MAC: mac}
                )

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_MAC): cv.string
            }),
            errors=errors,
            description_placeholders={"device_name": DEFAULT_NAME},
        )