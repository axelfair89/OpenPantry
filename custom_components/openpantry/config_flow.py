from __future__ import annotations
from typing import Any
import voluptuous as vol

from homeassistant.data_entry_flow import FlowResult
from homeassistant.config_entries import ConfigFlow, ConfigEntry
from homeassistant.const import CONF_NAME

from .const import DOMAIN, CONF_ENTRY_TITLE

class OpenPantryConfigFlow(ConfigFlow, domain=DOMAIN):
    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is not None:
            return self.async_create_entry(title=user_input.get(CONF_NAME, CONF_ENTRY_TITLE), data={})
        schema = vol.Schema({vol.Optional(CONF_NAME, default=CONF_ENTRY_TITLE): str})
        return self.async_show_form(step_id="user", data_schema=schema)
