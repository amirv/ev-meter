#!/usr/bin/env python3
"""
Test the config flow validation with enhanced error handling.
"""

import asyncio
import logging
import sys

# Add paths
sys.path.insert(0, "/home/amirv/git/ev-meter/custom_components/evmeter")
sys.path.insert(0, "/home/amirv/git/evmeter-client")

from config_flow import validate_input

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def test_config_flow():
    """Test config flow validation."""
    print("=" * 60)
    print("Testing Config Flow Validation")
    print("=" * 60)

    # Test data
    test_data = {"charger_id": "NONEXISTENT_CHARGER_123", "user_id": "TEST_USER_456"}

    print(f"Testing with data: {test_data}")
    print()

    try:
        # This should now succeed even if charger doesn't respond (timeout)
        result = await validate_input(None, test_data)  # hass can be None for this test
        print(f"✅ Validation succeeded: {result}")
        print("The integration setup should work now!")
        return True

    except ConnectionError as e:
        print(f"❌ Validation failed with ConnectionError: {e}")
        print("This indicates a real MQTT connection problem.")
        return False

    except Exception as e:
        print(f"❌ Validation failed with unexpected error: {e}")
        print(f"Exception type: {type(e).__name__}")
        return False


if __name__ == "__main__":
    success = asyncio.run(test_config_flow())
    if not success:
        sys.exit(1)
