# Guide for AI Assistants

This document provides context for AI assistants (like GitHub Copilot) to help them understand the project structure and make effective contributions.

## Project Overview

This repository contains two main components:
1.  **`evmeter_client`**: A Python library for communicating with EV-Meter chargers via MQTT.
2.  **`custom_components/evmeter`**: A Home Assistant integration that uses the `evmeter_client`.

## Core Logic Locations

-   **MQTT Communication**: `evmeter_client/client.py`. The `EVMeterClient` class handles all MQTT publishing and subscribing.
-   **Data Models**: `evmeter_client/models.py`. Dataclasses like `ChargerStatus` and `ChargerMetrics` define the structure of data received from the charger.
-   **HA Integration Setup**: `custom_components/evmeter/__init__.py`. The `async_setup_entry` function initializes the integration.
-   **HA Coordinator**: `custom_components/evmeter/coordinator.py`. The `EVMeterCoordinator` is responsible for polling the charger for data.
-   **HA Entities**: `custom_components/evmeter/sensor.py`. This is where Home Assistant sensor entities are defined.
-   **HA Configuration**: `custom_components/evmeter/config_flow.py`. This file manages the UI for setting up the integration.

## House Rules

1.  **Keep the Library Agnostic**: The `evmeter_client` library **must not** have any dependencies on Home Assistant. It should be a generic, reusable Python package.
2.  **Use the Coordinator**: In the Home Assistant integration, all data fetching must go through the `EVMeterCoordinator`. Entities should not make their own API calls.
3.  **Type Hints Everywhere**: All code should be fully type-hinted and pass `mypy` checks.
4.  **Use Placeholders for Unknowns**: For unknown MQTT topics, payload formats, or other protocol details, use descriptive placeholders and add a `TODO:` comment.
5.  **No Secrets in Code**: Do not hardcode credentials, tokens, or other secrets. These should be configured by the user via the config flow.

## Git Workflow

When the user asks you to commit changes:
-   **Execute the git commands** directly using the terminal, don't just suggest them.
-   Use `git add -u` to stage all modified files.
-   Write clear, descriptive commit messages following the conventional commits format (e.g., `feat:`, `fix:`, `docs:`, `refactor:`).
-   Example: `git add -u && git commit -m "docs: update architecture documentation"`

## Common Tasks

### How to Add a New Sensor

1.  **Update `evmeter_client`**:
    -   If the new sensor requires a new data point, add the corresponding field to a model in `evmeter_client/models.py`.
    -   Update the client in `evmeter_client/client.py` to parse this new field from the MQTT response payload.

2.  **Update the HA Integration**:
    -   In `custom_components/evmeter/sensor.py`, add a new `SensorEntityDescription` to the `SENSOR_TYPES` tuple. Define its `key`, `name`, `device_class`, etc.
    -   In the `EVMeterSensor` class, add logic to the `native_value` property to retrieve the new data point from the coordinator's data.
    -   In `custom_components/evmeter/translations/en.json`, add a friendly name for the new sensor under `entity.sensor`.

### How to Change MQTT Topics or Payloads

1.  **Modify `evmeter_client/config.py`**: Update the topic templates in the `EVMeterConfig` dataclass.
2.  **Modify `evmeter_client/client.py`**:
    -   Adjust the command payload structure in the `_send_command` method.
    -   Adjust the response parsing logic in `get_charger_status` and `get_charger_metrics`.
3.  **Review `custom_components/evmeter/config_flow.py`**: If the changes require new user configuration (e.g., a new topic base), update the `STEP_USER_DATA_SCHEMA`.
