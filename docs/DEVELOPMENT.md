# Development Guide

This guide provides instructions for setting up the development environment, running tests, and contributing to the project.

## Setup

### Prerequisites

-   Python 3.11+
-   Poetry

### Installation

1.  **Clone the repository**:
    ```bash
    git clone https://github.com/TODO-USERNAME/ev-meter.git
    cd ev-meter
    ```

2.  **Install dependencies**:
    Poetry will create a virtual environment and install all required packages.
    ```bash
    poetry install
    ```

3.  **Activate pre-commit hooks**:
    This will run linting and formatting checks automatically before each commit.
    ```bash
    poetry run pre-commit install
    ```

## Running Tools

All tools are run via `poetry run`.

-   **Run tests**:
    ```bash
    poetry run pytest
    ```

-   **Run linting (Ruff)**:
    ```bash
    poetry run ruff check .
    ```

-   **Run formatting (Black)**:
    ```bash
    poetry run black .
    ```

-   **Run static type checking (Mypy)**:
    ```bash
    poetry run mypy .
    ```

## Testing with a Local Home Assistant Instance

To test the integration in a real Home Assistant environment:

1.  **Set up a Home Assistant Core development environment.**
    Follow the official guide: [Setting up your development environment](https://developers.home-assistant.io/docs/development_environment/).

2.  **Link your custom component.**
    Create a symbolic link from your Home Assistant configuration's `custom_components` directory to this repository's `custom_components/evmeter`.

    ```bash
    # Example from within your HA config directory
    ln -s /path/to/your/ev-meter/custom_components/evmeter ./custom_components/evmeter
    ```

3.  **Start Home Assistant.**
    Run `hass` from your development environment.

4.  **Add the integration.**
    Go to Settings -> Devices & Services -> Add Integration and search for "EV-Meter EV Charger".

## Contribution Guidelines

-   Follow the code style enforced by Black and Ruff.
-   Ensure all tests pass before submitting a pull request.
-   Keep the `evmeter_client` library independent of Home Assistant.
-   Update documentation and add tests for new features.
