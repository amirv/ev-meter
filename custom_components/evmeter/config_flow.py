"""Config flow for EV-Meter EV Charger integration."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from evmeter_client import EVMeterClient, EVMeterConfig
from evmeter_client.exceptions import EVMeterError, EVMeterTimeoutError

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
    _LOGGER.debug("Starting connection validation")
    _LOGGER.debug(f"Charger ID: {data['charger_id']}")
    _LOGGER.debug(f"User ID: {data['user_id']}")

    # Create client with hardcoded MQTT settings per PRD
    config = EVMeterConfig(
        user_id=data["user_id"],
    )

    _LOGGER.debug(f"MQTT Config - Host: {config.mqtt_host}:{config.mqtt_port}")
    _LOGGER.debug(f"MQTT Config - Username: {config.mqtt_username}")
    _LOGGER.debug(
        f"MQTT Config - Response topic: {config.response_topic_template.format(user_id=data['user_id'])}"
    )

    client = EVMeterClient(config)

    try:
        _LOGGER.debug("Attempting MQTT connection...")
        # Test connection and command
        await client.connect()
        _LOGGER.debug("MQTT connection successful")

        _LOGGER.debug(
            f"Testing charger status request for charger {data['charger_id']}"
        )
        # Test that we can get status from the charger
        status = await client.get_charger_status(data["charger_id"])
        _LOGGER.debug(f"Charger status response received: {status}")

        await client.disconnect()
        _LOGGER.debug("MQTT disconnection successful")

    except EVMeterTimeoutError as e:
        _LOGGER.warning(f"Timeout during charger status request: {e}")
        _LOGGER.warning(
            "This could mean the charger ID is incorrect or the charger is offline"
        )
        _LOGGER.warning(
            "However, MQTT connection was successful, so we'll allow the setup to continue"
        )

        # For timeout errors, we still consider the setup successful since MQTT connection worked
        # The charger might just be offline or the ID might be wrong, but that's a runtime issue
        try:
            await client.disconnect()
        except Exception:
            pass  # Ignore disconnect errors

    except EVMeterError as e:
        _LOGGER.error(f"EVMeterError during validation: {e}")
        _LOGGER.error(f"Error type: {type(e).__name__}")
        if hasattr(e, "__cause__") and e.__cause__:
            _LOGGER.error(f"Underlying cause: {e.__cause__}")

        # Check if this is a connection-related error vs. a timeout/charger error
        if "connection" in str(e).lower() or "connect" in str(e).lower():
            raise ConnectionError from e
        else:
            # Other EVMeter errors (like protocol errors) shouldn't block setup
            _LOGGER.warning(
                "Non-connection error during validation, allowing setup to continue"
            )
            try:
                await client.disconnect()
            except Exception:
                pass

    except Exception as e:
        _LOGGER.error(f"Unexpected error during validation: {e}")
        _LOGGER.error(f"Error type: {type(e).__name__}")

        # Only treat actual connection/network errors as setup failures
        if any(
            keyword in str(e).lower()
            for keyword in ["connection", "network", "dns", "resolve", "connect"]
        ):
            raise ConnectionError from e
        else:
            _LOGGER.warning(
                "Non-connection error during validation, allowing setup to continue"
            )
            try:
                await client.disconnect()
            except Exception:
                pass

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
            _LOGGER.debug(f"Processing user input: {user_input}")
            try:
                info = await validate_input(self.hass, user_input)
                _LOGGER.debug(f"Validation successful: {info}")
            except ConnectionError as e:
                _LOGGER.error(f"Connection error during setup: {e}")
                # Try to categorize the error for better user feedback
                error_msg = str(e).lower()
                if "timeout" in error_msg or "timed out" in error_msg:
                    errors["base"] = "timeout"
                elif "name or service not known" in error_msg or "dns" in error_msg:
                    errors["base"] = "network_unreachable"
                elif "authentication" in error_msg or "auth" in error_msg:
                    errors["base"] = "auth_failed"
                elif "connection refused" in error_msg or "unreachable" in error_msg:
                    errors["base"] = "network_unreachable"
                else:
                    errors["base"] = "cannot_connect"
            except Exception as e:  # pylint: disable=broad-except
                _LOGGER.exception(f"Unexpected exception during setup: {e}")
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(user_input["charger_id"])
                self._abort_if_unique_id_configured()
                return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )
