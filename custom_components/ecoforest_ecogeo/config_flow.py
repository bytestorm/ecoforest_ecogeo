"""Config flow for Ecoforest integration."""

from __future__ import annotations

import logging
from typing import Any

from pyecoforest.exceptions import EcoforestAuthenticationRequired
import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_USERNAME, CONF_ALIAS

from .const import DOMAIN, MANUFACTURER
from .overrides.api import EcoGeoApi

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Optional(CONF_ALIAS): str,
    }
)


class EcoForestEcoGeoConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ecoforest."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                api = EcoGeoApi(
                    user_input[CONF_HOST],
                    user_input[CONF_USERNAME],
                    user_input[CONF_PASSWORD],
                )
                device = await api.get()
            except EcoforestAuthenticationRequired:
                errors["base"] = "invalid_auth"
            except Exception:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "cannot_connect"
            else:
                device_id = device.model_name
                title = f"{MANUFACTURER} {device.model_name}"

                if CONF_ALIAS in user_input:
                    device_id = user_input[CONF_ALIAS]
                    title = f"{title} ({user_input[CONF_ALIAS]})"

                await self.async_set_unique_id(device_id)
                self._abort_if_unique_id_configured()

                return self.async_create_entry(
                    title=title,
                    data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=STEP_USER_DATA_SCHEMA,
            errors=errors,
        )
