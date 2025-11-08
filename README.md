# EV-Meter Home Assistant Integration

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Home Assistant](https://img.shields.io/badge/Home%20Assistant-Compatible-blue.svg)](https://www.home-assistant.io/)

A Home Assistant custom integration for EV-Meter electric vehicle chargers that communicate via MQTT using the BLEWIFI protocol.

## Features

- **Real-time monitoring** of EV charging sessions via MQTT
- **25+ comprehensive sensors** with proper Home Assistant device classes
- **3-phase electrical measurements** (individual and average voltage/current)
- **Energy tracking** (session and lifetime totals with precise measurements)
- **Charger status and diagnostics** (warnings, errors, WiFi status, temperature)
- **Automatic device discovery** with firmware version detection
- **Professional sensor organization** with proper icons and units

## Sensors Provided

### Status & Control
- **Charger Status**: Current state (Idle, Charging, Error, etc.)
- **EV Status**: Connection status (Connected, Wants to Charge, etc.)
- **Charging State**: Detailed charging mode (1-Phase, 3-Phase, Waiting)
- **Phase Type**: Electrical configuration (Single/Three Phase)

### Power & Energy
- **Charging Power**: Real-time power consumption (kW)
- **Session Energy**: Current charging session energy (kWh)
- **Total Energy**: Lifetime energy delivered (kWh)

### 3-Phase Electrical (Individual & Average)
- **Voltage**: L1, L2, L3 and calculated average (V)
- **Current**: L1, L2, L3 and calculated average (A)
- **DLM Current**: Dynamic Load Management currents per phase

### Configuration & Limits
- **Set Current**: Configured current limit (A)
- **Circuit Breaker**: Rated circuit breaker capacity (A)

### System Information
- **Temperature**: Internal charger temperature (°C)
- **WiFi Network**: Connected network name
- **WiFi RSSI**: Signal strength (dBm)
- **Firmware Version**: System firmware version
- **Kubis Version**: Protocol version

### Diagnostics (Optional)
- **EVSE Status Code**: Technical status code
- **Warnings**: Count of active warnings
- **Errors**: Count of active errors
- **Ping Latency**: Network latency to charger (ms)
- **Peer Serial Number**: Internal serial number

## Installation

### Via HACS (Recommended)

1. In HACS, go to **Integrations**
2. Click the **⋮ menu** → **Custom repositories**
3. Add repository: `https://github.com/amirv/evmeter-hacs`
4. Category: **Integration**
5. Click **Add**
6. Find "EV-Meter" in HACS and click **Download**
7. **Restart Home Assistant**
8. Go to **Settings** → **Devices & Services** → **Add Integration**
9. Search for "EV-Meter" and follow the setup

### Manual Installation

1. Download the latest release from GitHub
2. Copy the `custom_components/evmeter` folder to your Home Assistant `custom_components` directory
3. Restart Home Assistant
4. Add the integration via Settings → Devices & Services

## Configuration

You'll need two pieces of information from your EV-Meter setup:

### 1. Charger ID
Your charger's unique identifier (12-character hex string, e.g., `7C9EBD4757CE`)

**How to find it:**
- Check your EV-Meter mobile app
- Look at MQTT topic names: `/BLEWIFI/Chargers/{CHARGER_ID}`
- Check the charger's web interface if available

### 2. User ID
Your unique user identifier (long hex string, e.g., `65336132363961312D356562652D343636372D393838312D646238373334663761316136`)

**How to find it:**
- Check MQTT logs for topic: `/BLEWIFI/users/{USER_ID}`
- Extract from your EV-Meter mobile app's network traffic
- Contact EV-Meter support if needed

### MQTT Settings
The integration uses hardcoded MQTT broker settings (as per EV-Meter protocol):
- **Host**: `iot.nayax.com`
- **Port**: `1883`
- **Username**: `deviceEV`
- **Password**: `ng4GycjMmuvpSJU6`

## Setup Process

1. **Add Integration**: Go to Settings → Devices & Services → Add Integration
2. **Search**: Find "EV-Meter" in the list
3. **Configure**: Enter your Charger ID and User ID
4. **Validation**: The integration will test the connection
5. **Complete**: Your charger will appear as a device with all sensors

## Device Information

The integration creates a single device representing your EV charger with:
- **Name**: EV-Meter Charger {CHARGER_ID}
- **Manufacturer**: EV-Meter
- **Model**: EV Charger
- **Firmware Version**: Automatically detected
- **Identifiers**: Based on your charger ID

## Data Updates

- **Update Frequency**: Every 60 seconds
- **Real-time Data**: Power, voltage, current measurements
- **Session Tracking**: Energy counters updated continuously
- **Status Changes**: Immediate updates when charger state changes

## Troubleshooting

### Integration Won't Install
- Ensure you've restarted Home Assistant after installation
- Check that `evmeter-client>=1.0.0` can be installed via pip
- Verify your Home Assistant version is 2024.1.0 or newer

### Connection Issues
- Verify your Charger ID and User ID are correct
- Check that your Home Assistant can reach `iot.nayax.com:1883`
- Ensure your charger is online and connected to WiFi

### Sensors Not Updating
- Check the integration logs for MQTT connection errors
- Verify your charger is actively sending data
- Try reloading the integration in Home Assistant

### Getting Help
- Check the [Issues](https://github.com/amirv/evmeter-hacs/issues) page
- Provide logs with debug logging enabled:
  ```yaml
  logger:
    logs:
      evmeter_client: debug
      custom_components.evmeter: debug
  ```

## Advanced Configuration

### Disabling Diagnostic Sensors
Some diagnostic sensors are disabled by default to reduce clutter. Enable them via:
1. Go to Settings → Devices & Services
2. Find your EV-Meter device
3. Click on disabled sensors to enable them

### Automation Examples

**Start charging notification:**
```yaml
automation:
  - alias: "EV Started Charging"
    trigger:
      - platform: state
        entity_id: sensor.charger_status
        to: "Charging"
    action:
      - service: notify.mobile_app
        data:
          message: "EV started charging at {{ states('sensor.charging_power') }}kW"
```

**High power alert:**
```yaml
automation:
  - alias: "High Power Charging Alert"
    trigger:
      - platform: numeric_state
        entity_id: sensor.charging_power
        above: 10  # kW
    action:
      - service: notify.mobile_app
        data:
          message: "High power charging: {{ states('sensor.charging_power') }}kW"
```

## Library

This integration uses the [evmeter-client](https://pypi.org/project/evmeter-client/) Python library, which is available on PyPI for other projects to use.

## Development

For development and testing, this repository uses Poetry:

1. **Install Dependencies**:
   ```bash
   poetry install
   ```

2. **Run Tests**:
   ```bash
   poetry run pytest
   ```

3. **Activate Pre-commit Hooks**:
   ```bash
   poetry run pre-commit install
   ```

See the `docs/` directory for detailed architecture, development, and contribution guides.

## Contributing

Contributions are welcome! Please check the [contributing guidelines](CONTRIBUTING.md) and feel free to submit pull requests or issues.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v2.2.0
- **MINOR**: Version minor release
- TODO: Add specific changes for this release
### v2.1.0
- **MINOR**: Version minor release
- TODO: Add specific changes for this release
### v2.0.2
- **FIX**: Updated to require evmeter-client>=1.1.1
- Fixes critical parser errors with MQTT message handling
- Improved error handling and diagnostics

### v2.0.1
- **FIX**: Removed zip_release from hacs.json to fix HACS download issues
- Integration files are directly in repository, no zip file needed

### v2.0.0
- **BREAKING CHANGE**: Converted to use evmeter-client pip package dependency
- Removed embedded library code for cleaner architecture
- Updated manifest to require evmeter-client>=1.0.0 from PyPI
- Added comprehensive pytest-asyncio testing framework
- Updated documentation for professional HACS deployment

### v1.0.0
- Initial HACS-ready release
- Uses evmeter-client library from PyPI
- 25+ comprehensive sensors
- Real-time MQTT monitoring
- Complete 3-phase electrical measurements
- Professional Home Assistant integration

---

**Note**: This integration requires an EV-Meter compatible electric vehicle charger. Visit [EV-Meter](https://evmeter.com) for more information about supported hardware.
