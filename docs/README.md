# EV-Meter Client & Home Assistant Integration Docs

This directory contains detailed documentation for the `evmeter_client` library and the Home Assistant integration.

## Overview

- **`evmeter_client`**: An asynchronous Python library to communicate with the EV-Meter MQTT backend.
- **`custom_components/evmeter`**: A Home Assistant integration that uses `evmeter_client` to expose charger data as entities.

## Quickstart

1.  **Install Dependencies**:
    ```bash
    poetry install
    ```

2.  **Run Tests**:
    ```bash
    poetry run pytest
    ```

3.  **Activate Pre-commit Hooks**:
    ```bash
    poetry run pre-commit install
    ```

## Home Assistant Installation (HACS)

1.  Open HACS in Home Assistant.
2.  Go to "Integrations" and click the three dots in the top right corner, then select "Custom repositories".
3.  Paste the URL of this repository into the "Repository" field.
4.  Select "Integration" as the category.
5.  Click "Add".
6.  The "EV-Meter EV Charger" integration will now be available to install.

## EV-Meter Protocol

The integration communicates with EV-Meter chargers via an MQTT broker.

- **TODO**: Describe the MQTT topics used.
- **TODO**: Describe the expected payload for commands and responses.
- **TODO**: List the data points available (e.g., charging power, energy, status).
