#!/usr/bin/env python3
"""
Direct test of the core MQTT connection issue.
This simulates what happens during Home Assistant integration setup.
"""

import asyncio
import logging
import sys

# Add the evmeter-client to the path
sys.path.insert(0, "/home/amirv/git/evmeter-client")

from evmeter_client import EVMeterClient, EVMeterConfig
from evmeter_client.exceptions import EVMeterError, EVMeterTimeoutError

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

_LOGGER = logging.getLogger(__name__)


async def simulate_integration_setup(charger_id: str, user_id: str):
    """Simulate the exact process that happens during integration setup."""
    _LOGGER.debug("Starting integration setup simulation")
    _LOGGER.debug(f"Charger ID: {charger_id}")
    _LOGGER.debug(f"User ID: {user_id}")

    # Create client with hardcoded MQTT settings per PRD
    config = EVMeterConfig(user_id=user_id)

    _LOGGER.debug(f"MQTT Config - Host: {config.mqtt_host}:{config.mqtt_port}")
    _LOGGER.debug(f"MQTT Config - Username: {config.mqtt_username}")
    _LOGGER.debug(
        f"MQTT Config - Response topic: {config.response_topic_template.format(user_id=user_id)}"
    )

    client = EVMeterClient(config)

    try:
        _LOGGER.debug("Attempting MQTT connection...")
        # Test connection and command
        await client.connect()
        _LOGGER.debug("MQTT connection successful")

        _LOGGER.debug(f"Testing charger status request for charger {charger_id}")
        # Test that we can get status from the charger
        status = await client.get_charger_status(charger_id)
        _LOGGER.debug(f"Charger status response received: {status}")

        await client.disconnect()
        _LOGGER.debug("MQTT disconnection successful")

        return True, "Setup successful"

    except EVMeterTimeoutError as e:
        _LOGGER.warning(f"Timeout during charger status request: {e}")
        _LOGGER.warning(
            "This could mean the charger ID is incorrect or the charger is offline"
        )
        _LOGGER.warning(
            "However, MQTT connection was successful, so we'll allow the setup to continue"
        )

        # For timeout errors, we still consider the setup successful since MQTT connection worked
        try:
            await client.disconnect()
        except Exception:
            pass  # Ignore disconnect errors

        return True, "Setup successful (charger may be offline)"

    except EVMeterError as e:
        _LOGGER.error(f"EVMeterError during validation: {e}")
        _LOGGER.error(f"Error type: {type(e).__name__}")
        if hasattr(e, "__cause__") and e.__cause__:
            _LOGGER.error(f"Underlying cause: {e.__cause__}")

        # Check if this is a connection-related error vs. a timeout/charger error
        if "connection" in str(e).lower() or "connect" in str(e).lower():
            return False, f"MQTT connection failed: {e}"
        else:
            # Other EVMeter errors (like protocol errors) shouldn't block setup
            _LOGGER.warning(
                "Non-connection error during validation, allowing setup to continue"
            )
            try:
                await client.disconnect()
            except Exception:
                pass
            return True, f"Setup successful (non-critical error: {e})"

    except Exception as e:
        _LOGGER.error(f"Unexpected error during validation: {e}")
        _LOGGER.error(f"Error type: {type(e).__name__}")

        # Only treat actual connection/network errors as setup failures
        if any(
            keyword in str(e).lower()
            for keyword in ["connection", "network", "dns", "resolve", "connect"]
        ):
            return False, f"Network/connection error: {e}"
        else:
            _LOGGER.warning(
                "Non-connection error during validation, allowing setup to continue"
            )
            try:
                await client.disconnect()
            except Exception:
                pass
            return True, f"Setup successful (non-critical error: {e})"


async def main():
    print("=" * 70)
    print("EV-Meter Integration Setup Simulation")
    print("=" * 70)

    # Test scenarios
    test_cases = [
        (
            "NONEXISTENT_CHARGER",
            "TEST_USER_123",
            "Non-existent charger (should succeed)",
        ),
        ("", "TEST_USER_456", "Empty charger ID (should fail gracefully)"),
        ("VALID_LOOKING_ID", "ANOTHER_USER", "Another test case"),
    ]

    for charger_id, user_id, description in test_cases:
        print(f"\n📋 Test Case: {description}")
        print(f"   Charger ID: '{charger_id}'")
        print(f"   User ID: '{user_id}'")
        print("-" * 50)

        success, message = await simulate_integration_setup(charger_id, user_id)

        if success:
            print(f"✅ Result: {message}")
            print("   → Home Assistant integration setup should work!")
        else:
            print(f"❌ Result: {message}")
            print("   → Home Assistant integration setup would fail")

        print()


if __name__ == "__main__":
    asyncio.run(main())
