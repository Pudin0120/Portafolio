# ESP32 Telematics Unit

The NodeMCU folder contains the ESP32-based telematics unit described in the FOTA system documentation. It acts as a communication bridge between the remote server and the vehicle gateway.

## Responsibilities documented by the project

- Request and download firmware update files from the server.
- Decrypt the downloaded update payload.
- Forward update data to the vehicle gateway.
- Receive update-download requests from the user/gateway side.
- Send vehicle diagnostic information to the server.

## Source files

- MainECU_V1/MainECU_V1.ino — Arduino sketch entry point.
- Server.cpp/.h — server communication module.
- FileHandler.cpp/.h — update-file handling.
- Cipher.cpp/.h — cryptographic helper implementation.
- Base64.cpp/.h — Base64 encoding/decoding helpers.
- Debug.h — debug configuration.

## Development setup

Open the sketch in Arduino IDE or a compatible ESP32 toolchain. The repository documentation identifies an ESP32 module, but the exact board revision, Arduino core version, library versions, Wi-Fi settings, and gateway pin/protocol configuration must be confirmed from the hardware being used.

Before uploading:

1. Confirm the ESP32 board target and serial port.
2. Configure server endpoints and network credentials through a local, untracked configuration.
3. Verify the gateway wiring and communication framing.
4. Test download failures, partial files, invalid/corrupted images, and interrupted transfer behavior.
5. Never test firmware updates on a vehicle or production controller until rollback and authenticity checks have been validated.

## Security considerations

Encryption is not a substitute for firmware authenticity. A production FOTA implementation should verify a trusted digital signature before accepting an image, reject replayed or stale versions, and use protected key storage. Do not commit Wi-Fi passwords, API secrets, or cryptographic keys.

See the [root project overview](../README.md) for the complete system architecture.
