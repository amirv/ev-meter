# EV-Meter MQTT Protocol Specification

This document outlines the binary protocol used for communication with EV-Meter chargers over MQTT. It is based on analysis of the `sample` scripts and logs.

## 1. Overview

The integration communicates with the EV-Meter backend using a request/response pattern over MQTT.

1.  **Request**: The client publishes a command to a charger-specific topic.
2.  **Response**: The backend replies with a message on a user-specific topic. The payload of this message is a binary structure containing charger data.

## 2. MQTT Topics

-   **Command Topic**: `/BLEWIFI/Chargers/{charger_id}`
    -   The client publishes requests to this topic.
    -   `{charger_id}` is the unique ID of the charger (e.g., `EXAMPLE123456`).
-   **Response Topic**: `/BLEWIFI/users/{user_id}`
    -   The client subscribes to this topic to receive responses.
    -   `{user_id}` is the unique ID of the user/installation, in hex string format (e.g., `65336132...`).

## 3. Command Payload

The command payload is a hardcoded binary message used to request data. Its structure is as follows:

| Offset (Bytes) | Length (Bytes) | Description | Value (Hex) |
| :--- | :--- | :--- | :--- |
| 0-1 | 2 | Total length of the following data (little-endian) | `6100` (97 bytes) |
| 2-7 | 6 | Padding / Zeros | `000000000000` |
| 8-9 | 2 | Command Marker | `0724` |
| 10 | 1 | Separator | `00` |
| 11-47 | 37 | User UUID (ASCII string, null-padded) | `653361...` |
| 48-49 | 2 | Constant | `3000` |
| 50-98 | 49 | Static Token / Signature | `170904...` |

**Example Command Payload (Hex):**
`610000000000000007246578616D706C652D757365722D69642D313233342D3536313233343536373839414243444546...truncated for brevity...270000`

## 4. Response Payload

The response is a JSON object containing a `payload_base64` field. This field, when decoded, reveals a binary structure.

### 4.1. Outer Payload Structure

The decoded `payload_base64` has the following structure:

| Offset (Bytes) | Length (Bytes) | Description |
| :--- | :--- | :--- |
| 0-1 | 2 | Length of the inner payload (N), little-endian. |
| 2 to N+1 | N | The **Inner Payload** (contains the actual data). |
| N+2 to end | varies | Additional data, including the User UUID in ASCII. |

### 4.2. Inner Payload (`WorkingInfo`)

The **Inner Payload** contains the core charger data. Its structure is parsed when the first byte is `0x03`.

| Field | Offset (Bytes) | Length (Bytes) | Data Type | Multiplier | Unit | Notes |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Message Type** | 0 | 1 | Unsigned Int | | | Always `0x03` for WorkingInfo |
| **Charger Status** | 1 | 1 | Enum | | | See 4.3 |
| **EVSE Status** | 2-5 | 4 | Unsigned Int (LE) | | | Device identifier |
| **Kubis Version** | 6+ | Variable | Length-prefixed String | | | 2-byte length + N bytes ASCII |
| **EV Status** | | 1 | Enum | | | See 4.4 |
| **Charging State** | | 1 | Enum | | | See 4.5 |
| **Warnings** | | 1 | Unsigned Int | | | Warning flags |
| **Errors** | | 1 | Unsigned Int | | | Error flags |
| **Voltage (Ph 1)** | | 2 | Unsigned Int (LE) | 0.25 | V | Divide by 4.0 |
| **Voltage (Ph 2)** | | 2 | Unsigned Int (LE) | 0.25 | V | Divide by 4.0 |
| **Voltage (Ph 3)** | | 2 | Unsigned Int (LE) | 0.25 | V | Divide by 4.0 |
| **Current (Ph 1)** | | 2 | Unsigned Int (LE) | 0.1 | A | Divide by 10.0 |
| **Current (Ph 2)** | | 2 | Unsigned Int (LE) | 0.1 | A | Divide by 10.0 |
| **Current (Ph 3)** | | 2 | Unsigned Int (LE) | 0.1 | A | Divide by 10.0 |
| **Session Energy** | | 4 | Unsigned Int (LE) | 1 | Wh | |
| **Total Energy** | | 4 | Unsigned Int (LE) | 1 | Wh | |
| **Phase Type** | | 1 | Enum | | | See 4.6 |
| **Set Current** | | 1 | Unsigned Int | | A | |
| **Firmware Version** | | 2 | Unsigned Int (LE) | | | |
| **Limit** | | 4 | Unsigned Int (LE) | | | 0xFFFFFFFF = UNLIMITED |
| **WiFi Network** | | Variable | Length-prefixed String | | | 2-byte length + N bytes ASCII |
| **Grid Type** | | 1 | Enum | | | See 4.7 |
| **MQTT Type** | | 1 | Enum | | | See 4.8 |
| **Charger ID** | | 8 | Unsigned Int (LE) | | | |
| **Start Time** | | 8 | Unsigned Int (LE) | | ms | |
| **Scheduler Version** | | 4 | Unsigned Int (LE) | | | |
| **Circuit Breaker** | | 4 | Unsigned Int (LE) | | A | |
| **DLM Current (Ph 1)** | | 2 | Unsigned Int (LE) | 0.1 | A | Divide by 10.0 |
| **DLM Current (Ph 2)** | | 2 | Unsigned Int (LE) | 0.1 | A | Divide by 10.0 |
| **DLM Current (Ph 3)** | | 2 | Unsigned Int (LE) | 0.1 | A | Divide by 10.0 |
| **Temperature** | | 1 | Unsigned Int | | °C | |
| **Peer Serial Number** | | 4 | Unsigned Int (LE) | | | |
| **Avg Ping Latency** | | 4 | Unsigned Int (LE) | | ms | |

*LE: Little-Endian*

### 4.3. Charger Status Enum (Message Type Offset 1)

| Value | Meaning |
| :--- | :--- |
| 0 | NOT_CONNECTED |
| 1 | WANTS_TO_CHARGE |
| 2 | CONNECTED |

### 4.4. EV Status Enum

| Value | Meaning |
| :--- | :--- |
| 0x00 | UNKNOWN |
| 0x01 | NOT_CONNECTED |
| 0x02 | CONNECTED |
| 0x03 | WANTS_TO_CHARGE |
| 0x04 | NEED_TO_VENTILATE |
| 0x05 | ERROR_STATE |

### 4.5. Charging State Enum

| Value | Meaning |
| :--- | :--- |
| 0x00 | UNKNOWN |
| 0x01 | NOT_CHARGING |
| 0x02 | CHARGING_1_PHASE |
| 0x03 | CHARGING_3_PHASE |
| 0x04 | WAITING_FOR_EV_AO |
| 0x05 | ALWAYS_ON_1_PHASE |
| 0x06 | ALWAYS_ON_3_PHASE |
| 0x07 | WAITING_FOR_EV |

### 4.6. Phase Type Enum

| Value | Meaning |
| :--- | :--- |
| 0x00 | UNKNOWN |
| 0x01 | PHASE_1 |
| 0x02 | PHASE_3 |

### 4.7. Grid Type Enum

| Value | Meaning |
| :--- | :--- |
| 0x00 | UNKNOWN |
| 0x01 | TN_S |
| 0x02 | IT |
| 0x03 | USA_1F_IT |

### 4.8. MQTT Type Enum

| Value | Meaning |
| :--- | :--- |
| 0x00 | UNKNOWN |
| 0x01 | WORKING_PROPERLY |
| 0x02 | MQTT_NOT_CONFIGURED |
| 0x03 | UNABLE_TO_CONNECT_BROKER |
| 0x04 | UNABLE_TO_CONNECT_WIFI |
| 0x05 | UNABLE_TO_DETECT_WIFI |
| 0x06 | WIFI_NOT_CONNECTED |

---
This document should provide a solid foundation for parsing and understanding the data from the EV-Meter. I have saved it to `docs/PROTOCOL.md`.
