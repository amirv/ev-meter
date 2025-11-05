### Product Requirements Document: EV-Meter MQTT Integration

#### 1. Introduction

This document outlines the product requirements for an integration that connects to EV-Meter electric vehicle chargers via an MQTT backend. The primary goal is to fetch, parse, and expose charger status and metrics for monitoring and automation purposes.

The system operates on a request/response pattern over MQTT. The integration sends a command to a specific charger and processes the corresponding data received from the server.

#### 2. System Architecture & Data Flow

1.  **Initiate Request**: The integration publishes a command payload to a specific MQTT topic to request data for a charger (e.g., ` /BLEWIFI/Chargers/{charger_id}`).
2.  **Server Response**: The EV-Meter MQTT backend responds by publishing a message to a user-specific topic (e.g., `/BLEWIFI/users/{user_id}`).
3.  **Receive & Parse**: The integration listens on the response topic, receives the message, and parses the binary payload to extract structured sensor data.

#### 3. Functional Requirements

| ID | Requirement | Description |
| :--- | :--- | :--- |
| **FR-1** | **MQTT Connection** | The integration must connect to the MQTT broker at `iot.nayax.com` on port `1883`. |
| **FR-2** | **Authentication** | The connection must use the hardcoded credentials: <br/> - **Username**: `deviceEV` <br/> - **Password**: `ng4GycjMmuvpSJU6` |
| **FR-3** | **Data Request** | The integration must send commands to request data from a specific charger by publishing to the topic `/BLEWIFI/Chargers/{charger_id}`. |
| **FR-4** | **Data Reception** | The integration must subscribe to `/BLEWIFI/users/{user_id}` to receive response messages from the backend. |
| **FR-5** | **Payload Parsing** | The integration must decode the `payload_base64` field from the received JSON and parse the resulting binary data to extract structured sensor information. |

#### 4. Non-Functional Requirements

| ID | Requirement | Description |
| :--- | :--- | :--- |
| **NFR-1** | **Configuration** | MQTT broker details (server, port, username, password) shall be treated as constants and are not user-configurable. |
| **NFR-2** | **Security** | The MQTT username and password must be stored securely within the integration, preferably hashed, and not exposed in plain text. |
| **NFR-3** | **Error Handling** | The integration must gracefully handle connection failures, timeouts when waiting for a response, and errors during payload parsing. |
| **NFR-4** | **Performance** | The request-response cycle should be efficient to allow for near real-time data polling without overwhelming the MQTT broker. |

#### 5. Out of Scope

*   **User-Managed Credentials**: Users will not be able to provide their own MQTT credentials. The system relies on the predefined shared credentials.
*   **Direct Control Commands**: This phase of the integration is focused solely on monitoring (read-only). Sending control commands (e.g., start/stop charging) is not in scope.
*   **Dynamic Topic Configuration**: The MQTT topic structure is fixed and cannot be configured by the end-user.
