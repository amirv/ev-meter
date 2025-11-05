# EV-Meter Client & Home Assistant Integration

This repository contains a Python library and a Home Assistant custom integration for EV-Meter electric vehicle chargers.

- **`evmeter_client`**: An asynchronous Python library to communicate with the EV-Meter MQTT backend.
- **`custom_components/evmeter`**: A Home Assistant integration that uses `evmeter_client` to expose charger data as entities.

This project is designed for development with Poetry, VS Code, and follows modern Home Assistant and HACS best practices.

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

See the `docs/` directory for detailed architecture, development, and contribution guides.
