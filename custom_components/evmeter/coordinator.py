"""Data update coordinator for the EV-Meter integration."""

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from evmeter_client import EVMeterClient, EVMeterConfig, EVMeterError

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

    async def _async_update_data(self):
        """Fetch data from the EV-Meter client."""
        try:
            if not self.client._client:
                await self.client.connect()

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
        except EVMeterError as err:
            raise UpdateFailed(f"Error communicating with API: {err}") from err
