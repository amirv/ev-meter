"""Config flow for EV-Meter EV Charger integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from evmeter_client import EVMeterClient, EVMeterConfig
from evmeter_client.exceptions import EVMeterError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Per PRD: MQTT broker details are hardcoded, only charger_id and user_id are configurable
STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("charger_id"): str,
        vol.Required("user_id"): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """
    # Create client with hardcoded MQTT settings per PRD
    config = EVMeterConfig(
        user_id=data["user_id"],
    )
    client = EVMeterClient(config)

    try:
        # Test connection and command
        await client.connect()
        # Test that we can get status from the charger
        await client.get_charger_status(data["charger_id"])
        await client.disconnect()
    except EVMeterError as e:
        raise ConnectionError from e

    return {"title": f"EV-Meter Charger {data['charger_id']}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for EV-Meter EV Charger."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input["charger_id"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
