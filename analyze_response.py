#!/usr/bin/env python3
"""Analyze the response payload from the EV-Meter server."""

import asyncio
import logging
from evmeter_client import EVMeterClient, EVMeterConfig

# Enable debug logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s"
)

CHARGER_ID = "EXAMPLE123456"
USER_ID = "6578616D706C652D757365722D69642D31323334352D366578616D706C65"


async def analyze_response():
    """Get a response and analyze it in detail."""
    print("=" * 70)
    print("EV-Meter Response Analysis")
    print("=" * 70)

    config = EVMeterConfig(user_id=USER_ID)
    client = EVMeterClient(config)

    try:
        print("Connecting to MQTT broker...")
        await client.connect()
        print("✓ Connected!\n")

        await asyncio.sleep(1)

        print(f"Requesting data from charger {CHARGER_ID}...")
        command_payload = client._create_command_payload(CHARGER_ID)

        # Get raw response
        response = await client._send_command(CHARGER_ID, command_payload)

        print("\n" + "=" * 70)
        print("RAW RESPONSE ANALYSIS")
        print("=" * 70)

        # Show raw hex payload
        if "raw_payload" in response:
            raw_hex = response["raw_payload"]
            print(f"\nRaw Payload (hex): {raw_hex}")
            print(f"Length: {len(raw_hex) // 2} bytes")

            # Convert to bytes for detailed analysis
            raw_bytes = bytes.fromhex(raw_hex)

            print("\nHex dump:")
            for i in range(0, len(raw_bytes), 16):
                chunk = raw_bytes[i : i + 16]
                hex_str = " ".join(f"{b:02x}" for b in chunk)
                ascii_str = "".join(chr(b) if 32 <= b < 127 else "." for b in chunk)
                print(f"  {i:04x}: {hex_str:48s} {ascii_str}")

            print("\nByte-by-byte breakdown:")
            for i, byte in enumerate(raw_bytes[:20]):  # First 20 bytes
                print(
                    f"  Byte {i:2d}: 0x{byte:02x} ({byte:3d}) {chr(byte) if 32 <= byte < 127 else '.'}"
                )

        print("\n" + "=" * 70)
        print("PARSED DATA")
        print("=" * 70)

        for key, value in response.items():
            if key == "raw_payload":
                continue
            print(f"\n{key}:")
            if isinstance(value, dict):
                for k, v in value.items():
                    print(f"  {k}: {v}")
            else:
                print(f"  {value}")

        # If we have working_info, analyze it
        if "working_info" in response:
            print("\n" + "=" * 70)
            print("WORKING INFO DETAILS")
            print("=" * 70)
            wi = response["working_info"]

            print(f"\nVoltage: {wi.get('voltage', 0):.2f} V")
            print(f"Current: {wi.get('current', 0):.2f} A")
            print(f"Power: {wi.get('power', 0):.3f} kW")
            print(f"Energy: {wi.get('energy', 0):.3f} kWh")

        print("\n" + "=" * 70)

    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback

        traceback.print_exc()
    finally:
        await client.disconnect()
        print("\n✓ Disconnected\n")


if __name__ == "__main__":
    asyncio.run(analyze_response())
