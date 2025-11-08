#!/usr/bin/env python3
"""
Test script to debug MQTT connection issues with EV-Meter integration.
"""

import asyncio
import logging
import sys

# Add the evmeter-client to the path
sys.path.insert(0, "/home/amirv/git/evmeter-client")

from evmeter_client import EVMeterClient, EVMeterConfig

# Enable debug logging
logging.basicConfig(
    level=logging.DEBUG, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def test_connection():
    """Test MQTT connection with debug logging."""
    print("=" * 60)
    print("EV-Meter MQTT Connection Test")
    print("=" * 60)

    # Test configuration
    user_id = "TEST_USER_123"  # You can change this
    charger_id = "TEST_CHARGER_456"  # You can change this

    print(f"Testing with User ID: {user_id}")
    print(f"Testing with Charger ID: {charger_id}")
    print()

    # Create config and client
    config = EVMeterConfig(user_id=user_id)
    client = EVMeterClient(config)

    print("Configuration:")
    print(f"  MQTT Host: {config.mqtt_host}")
    print(f"  MQTT Port: {config.mqtt_port}")
    print(f"  MQTT Username: {config.mqtt_username}")
    print(f"  Response Topic: {config.response_topic_template.format(user_id=user_id)}")
    print(
        f"  Command Topic: {config.command_topic_template.format(charger_id=charger_id)}"
    )
    print()

    try:
        print("Step 1: Testing MQTT connection...")
        await client.connect()
        print("✅ MQTT connection successful!")

        print("\nStep 2: Testing charger status request...")
        try:
            status = await client.get_charger_status(charger_id)
            print(f"✅ Charger status request successful: {status}")
        except Exception as e:
            print(f"⚠️  Charger status request failed (this might be expected): {e}")
            print("This could be normal if the charger ID doesn't exist.")

        print("\nStep 3: Disconnecting...")
        await client.disconnect()
        print("✅ Disconnection successful!")

        print("\n🎉 All tests completed successfully!")
        print("The MQTT connection is working. The integration should work.")

    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        print(f"Exception type: {type(e).__name__}")
        if hasattr(e, "__cause__") and e.__cause__:
            print(f"Underlying cause: {e.__cause__}")
        print("\nThis indicates a real connection problem.")
        return False

    return True


if __name__ == "__main__":
    success = asyncio.run(test_connection())
    if not success:
        sys.exit(1)
