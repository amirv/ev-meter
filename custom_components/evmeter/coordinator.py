"""Data update coordinator for the EV-Meter integration."""

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from evmeter_client import EVMeterClient, EVMeterConfig
from evmeter_client.exceptions import EVMeterError, EVMeterTimeoutError

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


class EVMeterCoordinator(DataUpdateCoordinator):
    """Manages fetching data from the EV-Meter client."""

    def __init__(
        self, hass: HomeAssistant, config_data: dict[str, Any], charger_id: str
    ):
        """Initialize the data update coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=f"EVMeter-{charger_id}",
            update_interval=timedelta(seconds=60),  # Update every minute
        )

        # Per PRD: MQTT settings are hardcoded
        client_config = EVMeterConfig(
            user_id=config_data["user_id"],
        )
        self.client = EVMeterClient(client_config)
        self.charger_id = charger_id
        self.device_info = DeviceInfo(
            identifiers={(DOMAIN, self.charger_id)},
            name=f"EV-Meter Charger {self.charger_id}",
            manufacturer="EV-Meter",
            model="EV Charger",
        )

    async def async_shutdown(self):
        """Clean shutdown of the coordinator."""
        _LOGGER.debug("Shutting down EVMeter coordinator for %s", self.charger_id)
        try:
            await self.client.disconnect()
        except Exception as err:
            _LOGGER.debug("Error during coordinator shutdown: %s", err)

    async def _async_update_data(self):
        """Fetch data from the EV-Meter client."""
        try:
            # Always ensure we have a valid connection
            await self._ensure_connected()

            status = await self.client.get_charger_status(self.charger_id)
            metrics = await self.client.get_charger_metrics(self.charger_id)

            # Update device info with firmware version on first successful fetch
            if status.kubis_version and not self.device_info.get("sw_version"):
                self.device_info = DeviceInfo(
                    identifiers={(DOMAIN, self.charger_id)},
                    name=f"EV-Meter Charger {self.charger_id}",
                    manufacturer="EV-Meter",
                    model="EV Charger",
                    sw_version=status.kubis_version,
                )

            return {
                "status": status,
                "metrics": metrics,
            }
        except (EVMeterError, EVMeterTimeoutError) as err:
            # If we get a connection error, try to reconnect on next update
            error_msg = str(err).lower()
            if any(
                keyword in error_msg
                for keyword in [
                    "not currently connected",
                    "connection",
                    "mqtt",
                    "disconnected",
                    "code:4",  # MQTT code 4 is "not connected"
                ]
            ):
                _LOGGER.warning(
                    "MQTT connection lost (%s), will attempt reconnection on next update",
                    err,
                )
                try:
                    await self.client.disconnect()
                except Exception:
                    pass  # Ignore disconnect errors
                self.client._client = None  # Reset client state
            elif isinstance(err, EVMeterTimeoutError):
                _LOGGER.debug("Charger timeout (may be offline): %s", err)
            else:
                _LOGGER.error("Unexpected error: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err

    async def _ensure_connected(self):
        """Ensure the MQTT client is connected and ready."""
        try:
            # Check if client exists and try a simple operation to test connection
            if not self.client._client:
                _LOGGER.debug("No MQTT client found, establishing connection")
                await self.client.connect()
            else:
                # Test if the connection is still alive by checking client state
                # If the client exists but is disconnected, aiomqtt will raise an error
                try:
                    # This will raise an exception if not connected
                    if (
                        not hasattr(self.client._client, "_client")
                        or not self.client._client._client.is_connected()
                    ):
                        _LOGGER.info("MQTT client disconnected, reconnecting")
                        await self.client.disconnect()
                        await self.client.connect()
                except Exception:
                    # If we can't check connection state, assume disconnected and reconnect
                    _LOGGER.info("Unable to verify MQTT connection state, reconnecting")
                    try:
                        await self.client.disconnect()
                    except Exception:
                        pass
                    await self.client.connect()
        except Exception as err:
            _LOGGER.error("Failed to establish MQTT connection: %s", err)
            raise EVMeterError(f"Connection failed: {err}") from err
