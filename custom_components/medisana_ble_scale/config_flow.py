"""Config flow for BS440 BLE integration."""
import voluptuous as vol
import logging
from homeassistant import config_entries
from homeassistant.components.bluetooth import async_scanner_count
from homeassistant.helpers import config_validation as cv
from homeassistant.core import callback

from .const import DOMAIN, CONF_MAC, DEFAULT_NAME, CONF_USERS

_LOGGER = logging.getLogger(__name__)

class BS440ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for BS440 BLE."""

    VERSION = 1

    def __init__(self):
        """Initialize flow."""
        self.mac = None

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return BS440OptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step (MAC Address)."""
        errors = {}

        if user_input is not None:
            self.mac = user_input[CONF_MAC].upper()
            await self.async_set_unique_id(self.mac)
            self._abort_if_unique_id_configured()

            if async_scanner_count(self.hass) == 0:
                errors["base"] = "no_bluetooth_adapter"
            else:
                # Proceed to naming step
                return await self.async_step_names()

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required(CONF_MAC): cv.string
            }),
            errors=errors,
            description_placeholders={"device_name": DEFAULT_NAME},
        )

    async def async_step_names(self, user_input=None):
        """Handle the second step (User Naming)."""
        if user_input is not None:
            return self.async_create_entry(
                title=f"{DEFAULT_NAME} ({self.mac})",
                data={
                    CONF_MAC: self.mac,
                    CONF_USERS: user_input.get(CONF_USERS, "")
                }
            )

        return self.async_show_form(
            step_id="names",
            data_schema=vol.Schema({
                vol.Optional(CONF_USERS): cv.string
            })
        )

class BS440OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for the integration (editing names later)."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        # Fix: Store entry in _config_entry to avoid conflict with read-only property
        self._config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        # Fix: Reference _config_entry
        current_users = self._config_entry.options.get(
            CONF_USERS,
            self._config_entry.data.get(CONF_USERS, "")
        )

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema({
                vol.Optional(
                    CONF_USERS,
                    default=current_users
                ): cv.string
            })
        )