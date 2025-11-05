# Architecture

This document outlines the architecture of the `evmeter_client` library and the Home Assistant integration.

## `evmeter_client` Library

The `evmeter_client` is a standalone, asynchronous Python library responsible for all communication with the EV-Meter MQTT backend.

### Core Components

-   **`EVMeterClient`**: The main entry point for the library. It manages the MQTT connection, sends commands, and receives responses.
-   **`EVMeterConfig`**: A dataclass holding configuration for the client, such as MQTT broker details and topic templates.
-   **`models.py`**: Contains dataclasses (`ChargerStatus`, `ChargerMetrics`) that represent the data parsed from the charger's responses. These provide a clean, typed interface for consumers of the library.
-   **`exceptions.py`**: Defines custom exceptions for handling errors like timeouts or protocol issues.

### MQTT Communication

The client uses a request/response pattern over MQTT:
1.  A command (e.g., `get_status`) is published to a command topic (e.g., `evmeter/{charger_id}/command`).
2.  The client subscribes to a corresponding response topic (`evmeter/{charger_id}/response`).
3.  It waits for a response on that topic, using an `asyncio.Future` to correlate the request with the incoming message.
4.  When a response is received, its payload is parsed into one of the data models.

**TODO**: A more robust implementation should use a correlation ID within the MQTT payload to handle concurrent requests reliably.

## Home Assistant Integration

The `evmeter` integration connects the `evmeter_client` library to Home Assistant.

### Key Files

-   **`__init__.py`**: Sets up the integration from a config entry. It creates an `EVMeterClient` instance and a `DataUpdateCoordinator`.
-   **`config_flow.py`**: Manages the user configuration process through the Home Assistant UI. It collects MQTT broker details and the charger ID.
-   **`coordinator.py`**: The `EVMeterCoordinator` uses the `evmeter_client` to periodically fetch the latest data from the charger. This centralizes data fetching and reduces redundant API calls.
-   **`sensor.py`**: Defines the `SensorEntity` classes. Each sensor is linked to the coordinator and gets its state from the coordinated data.
-   **`const.py`**: Holds shared constants, most importantly the integration `DOMAIN`.
-   **`manifest.json`**: Declares the integration's metadata, dependencies, and requirements.

### Data Flow

1.  The user adds the integration via the config flow, providing MQTT details.
2.  `async_setup_entry` is called, which initializes the `EVMeterCoordinator`.
3.  The coordinator is stored in `hass.data[DOMAIN][entry.entry_id]`.
4.  The coordinator's `_async_update_data` method is called periodically. It uses the `EVMeterClient` to fetch status and metrics.
5.  Sensor entities are created and linked to the coordinator. They automatically update their state whenever the coordinator successfully fetches new data.
6.  Entities are grouped under a single Device in Home Assistant for a clean user experience.
