"""Sensor platform for the EV-Meter EV Charger integration."""

from __future__ import annotations

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    UnitOfElectricCurrent,
    UnitOfElectricPotential,
    UnitOfEnergy,
    UnitOfPower,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from evmeter_client.models import ChargerState

from .const import DOMAIN
from .coordinator import EVMeterCoordinator

# Define comprehensive sensor entity descriptions
SENSOR_TYPES: tuple[SensorEntityDescription, ...] = (
    # Status sensors
    SensorEntityDescription(
        key="status",
        name="Charger Status",
        icon="mdi:ev-station",
        device_class=SensorDeviceClass.ENUM,
        options=[e.value for e in ChargerState],
    ),
    SensorEntityDescription(
        key="ev_status",
        name="EV Status",
        icon="mdi:car-electric",
        device_class=SensorDeviceClass.ENUM,
    ),
    SensorEntityDescription(
        key="charging_state",
        name="Charging State",
        icon="mdi:battery-charging",
        device_class=SensorDeviceClass.ENUM,
    ),
    SensorEntityDescription(
        key="phase_type",
        name="Phase Type",
        icon="mdi:sine-wave",
        device_class=SensorDeviceClass.ENUM,
    ),
    # Power and energy sensors
    SensorEntityDescription(
        key="power",
        name="Charging Power",
        native_unit_of_measurement=UnitOfPower.KILO_WATT,
        device_class=SensorDeviceClass.POWER,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=2,
    ),
    SensorEntityDescription(
        key="session_energy",
        name="Session Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=3,
    ),
    SensorEntityDescription(
        key="total_energy",
        name="Total Energy",
        native_unit_of_measurement=UnitOfEnergy.KILO_WATT_HOUR,
        device_class=SensorDeviceClass.ENERGY,
        state_class=SensorStateClass.TOTAL_INCREASING,
        suggested_display_precision=1,
    ),
    # Voltage sensors (3-phase)
    SensorEntityDescription(
        key="voltage_ph1",
        name="Voltage Phase 1",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="voltage_ph2",
        name="Voltage Phase 2",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="voltage_ph3",
        name="Voltage Phase 3",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="voltage_avg",
        name="Average Voltage",
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        device_class=SensorDeviceClass.VOLTAGE,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    # Current sensors (3-phase)
    SensorEntityDescription(
        key="current_ph1",
        name="Current Phase 1",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="current_ph2",
        name="Current Phase 2",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="current_ph3",
        name="Current Phase 3",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    SensorEntityDescription(
        key="current_avg",
        name="Average Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        state_class=SensorStateClass.MEASUREMENT,
        suggested_display_precision=1,
    ),
    # Configuration sensors
    SensorEntityDescription(
        key="set_current",
        name="Set Current",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        icon="mdi:current-ac",
    ),
    SensorEntityDescription(
        key="circuit_breaker",
        name="Circuit Breaker",
        native_unit_of_measurement=UnitOfElectricCurrent.AMPERE,
        device_class=SensorDeviceClass.CURRENT,
        icon="mdi:fuse",
    ),
    # System sensors
    SensorEntityDescription(
        key="temperature",
        name="Temperature",
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    SensorEntityDescription(
        key="wifi_network",
        name="WiFi Network",
        icon="mdi:wifi",
    ),
    SensorEntityDescription(
        key="firmware_version",
        name="Firmware Version",
        icon="mdi:chip",
    ),
    SensorEntityDescription(
        key="kubis_version",
        name="Kubis Version",
        icon="mdi:information",
    ),
    # Diagnostic sensors
    SensorEntityDescription(
        key="warnings",
        name="Warnings",
        icon="mdi:alert-outline",
    ),
    SensorEntityDescription(
        key="errors",
        name="Errors",
        icon="mdi:alert-circle-outline",
    ),
    SensorEntityDescription(
        key="evse",
        name="EVSE ID",
        icon="mdi:identifier",
    ),
    SensorEntityDescription(
        key="ping_latency",
        name="Ping Latency",
        native_unit_of_measurement=UnitOfTime.MILLISECONDS,
        state_class=SensorStateClass.MEASUREMENT,
        icon="mdi:network",
        entity_registry_enabled_default=False,  # Diagnostic sensor
    ),
    SensorEntityDescription(
        key="grid_type",
        name="Grid Type",
        icon="mdi:transmission-tower",
        entity_registry_enabled_default=False,  # Diagnostic sensor
    ),
    SensorEntityDescription(
        key="mqtt_type",
        name="MQTT Status",
        icon="mdi:mqtt",
        entity_registry_enabled_default=False,  # Diagnostic sensor
    ),
    SensorEntityDescription(
        key="start_time",
        name="Start Time",
        icon="mdi:clock-start",
        entity_registry_enabled_default=False,  # Diagnostic sensor
    ),
    SensorEntityDescription(
        key="scheduler_version",
        name="Scheduler Version",
        icon="mdi:update",
        entity_registry_enabled_default=False,  # Diagnostic sensor
    ),
    SensorEntityDescription(
        key="peer_serial",
        name="Peer Serial Number",
        icon="mdi:serial-port",
        entity_registry_enabled_default=False,  # Diagnostic sensor
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: EVMeterCoordinator = hass.data[DOMAIN][entry.entry_id]
    entities = [EVMeterSensor(coordinator, description) for description in SENSOR_TYPES]
    async_add_entities(entities)


class EVMeterSensor(CoordinatorEntity[EVMeterCoordinator], SensorEntity):
    """Representation of an EV-Meter sensor."""

    def __init__(
        self,
        coordinator: EVMeterCoordinator,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{coordinator.charger_id}_{description.key}"
        self._attr_device_info = coordinator.device_info

    @property
    def native_value(self) -> str | int | float | None:
        """Return the state of the sensor."""
        if self.coordinator.data is None:
            return None

        status = self.coordinator.data.get("status")
        metrics = self.coordinator.data.get("metrics")
        key = self.entity_description.key

        # Status-based sensors
        if key == "status" and status:
            return status.state.value
        if key == "ev_status" and status:
            return status.ev_status.value
        if key == "charging_state" and status:
            return status.charging_state.value
        if key == "phase_type" and status:
            return status.phase_type.value

        # Power and energy sensors
        if key == "power" and metrics:
            return metrics.power_kw
        if key == "session_energy" and metrics:
            return metrics.session_energy_kwh
        if key == "total_energy" and metrics:
            return metrics.total_energy_kwh

        # Three-phase voltage sensors
        if key == "voltage_ph1" and metrics:
            return metrics.voltage_ph1
        if key == "voltage_ph2" and metrics:
            return metrics.voltage_ph2
        if key == "voltage_ph3" and metrics:
            return metrics.voltage_ph3
        if key == "voltage_avg" and metrics:
            return metrics.voltage_avg

        # Three-phase current sensors
        if key == "current_ph1" and metrics:
            return metrics.current_ph1
        if key == "current_ph2" and metrics:
            return metrics.current_ph2
        if key == "current_ph3" and metrics:
            return metrics.current_ph3
        if key == "current_avg" and metrics:
            return metrics.current_avg

        # Configuration sensors
        if key == "set_current" and status:
            return status.set_current
        if key == "circuit_breaker" and status:
            return status.circuit_breaker

        # System sensors
        if key == "temperature" and metrics:
            return metrics.temperature
        if key == "wifi_network" and status:
            return status.wifi_network
        if key == "firmware_version" and status:
            return status.firmware_version
        if key == "kubis_version" and status:
            return status.kubis_version

        # Diagnostic sensors
        if key == "warnings" and status:
            return status.warnings
        if key == "errors" and status:
            return status.errors
        if key == "evse" and status:
            return status.evse
        if key == "ping_latency" and metrics:
            return metrics.avg_ping_latency

        # Additional diagnostic sensors
        if key == "grid_type" and status:
            return status.grid_type.value
        if key == "mqtt_type" and status:
            return status.mqtt_type.value
        if key == "start_time" and status:
            return status.start_time
        if key == "scheduler_version" and status:
            return status.scheduler_version
        if key == "peer_serial" and metrics:
            return metrics.peer_serial_number

        return None
