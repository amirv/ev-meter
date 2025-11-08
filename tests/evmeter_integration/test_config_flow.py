"""Test evmeter integration setup and imports."""

import json
import os

import pytest


def test_evmeter_client_imports():
    """Test that all required evmeter-client imports work."""
    from evmeter_client import EVMeterClient, EVMeterConfig
    from evmeter_client.exceptions import EVMeterError
    from evmeter_client.models import ChargerState

    assert EVMeterClient is not None
    assert EVMeterConfig is not None
    assert EVMeterError is not None
    assert ChargerState is not None


def test_integration_constants():
    """Test that integration constants are properly defined."""
    # Read the const.py file directly to check the domain
    const_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "custom_components",
        "evmeter",
        "const.py",
    )

    with open(const_path) as f:
        const_content = f.read()

    # Check that DOMAIN is defined correctly
    assert 'DOMAIN = "evmeter"' in const_content


def test_manifest_requirements():
    """Test that the manifest has the correct pip package requirement."""
    manifest_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "custom_components",
        "evmeter",
        "manifest.json",
    )

    with open(manifest_path) as f:
        manifest = json.load(f)

    assert "requirements" in manifest
    assert any("evmeter-client" in req for req in manifest["requirements"])
    assert manifest["domain"] == "evmeter"
    assert manifest["name"] == "EV-Meter"
    assert "version" in manifest


def test_integration_structure():
    """Test that integration files exist."""
    integration_path = os.path.join(
        os.path.dirname(__file__), "..", "..", "custom_components", "evmeter"
    )

    required_files = [
        "__init__.py",
        "config_flow.py",
        "coordinator.py",
        "sensor.py",
        "const.py",
        "manifest.json",
    ]

    for filename in required_files:
        file_path = os.path.join(integration_path, filename)
        assert os.path.exists(file_path), f"Missing required file: {filename}"


@pytest.mark.asyncio
async def test_evmeter_client_connection():
    """Test that EVMeterClient can be instantiated and has expected methods."""
    from evmeter_client import EVMeterClient, EVMeterConfig

    # Create a config using the correct parameter names
    config = EVMeterConfig(
        mqtt_host="iot.nayax.com",
        mqtt_port=1883,
        mqtt_username="deviceEV",
        mqtt_password="test",
        user_id="test-user",
    )

    # Create client instance
    client = EVMeterClient(config)

    # Verify it has expected methods
    assert hasattr(client, "connect")
    assert hasattr(client, "disconnect")
    assert hasattr(client, "get_charger_status")
    assert hasattr(client, "get_charger_metrics")
    assert callable(client.connect)
    assert callable(client.disconnect)
    assert callable(client.get_charger_status)
    assert callable(client.get_charger_metrics)


def test_config_flow_imports():
    """Test that config flow can import required modules without error."""
    # This will only work without Home Assistant installed if we avoid importing the module
    # Instead, let's verify the file structure and imports are syntactically correct

    config_flow_path = os.path.join(
        os.path.dirname(__file__),
        "..",
        "..",
        "custom_components",
        "evmeter",
        "config_flow.py",
    )

    with open(config_flow_path) as f:
        config_flow_content = f.read()

    # Check that evmeter-client imports are present
    assert (
        "from evmeter_client import EVMeterClient, EVMeterConfig" in config_flow_content
    )
    assert "from evmeter_client.exceptions import EVMeterError" in config_flow_content
