# FOTA Graduation Project — Secure Firmware Update and Vehicle Diagnostics

This project is a distributed embedded system prototype for firmware-over-the-air (FOTA) updates and vehicle diagnostics. The repository is split into embedded firmware, a telematics communication unit, a Raspberry Pi user interface, a Firebase-backed server tool, hardware design files, and supporting documentation.

## System overview

| Component | Folder | Responsibility |
| --- | --- | --- |
| Embedded firmware | ARM/ | Hardware abstraction, peripheral drivers, RTOS tasks, application ECUs, and bootloader/update flow |
| Telematics unit | NodeMCU/ | ESP32-based bridge between the server and the vehicle gateway |
| User interface | RPI/ | Raspberry Pi 4 touchscreen UI for notifications, diagnostics, and vehicle-facing utilities |
| Server and database manager | Server/ | PyQt5 desktop tool and Firebase integration for firmware/update data |
| Hardware design | Hardware/ | Altium schematic and library files |
| Supporting material | Documentation/, assets/ | Project presentation, diagrams, screenshots, and documentation assets |

The architecture and behavior below are summarized from the component READMEs in this repository. They are not a claim that the complete hardware/software system has been built or tested in the current environment.

## Main workflows described

### Firmware update

1. The server side manages update files and related metadata.
2. The ESP32 telematics unit communicates with the server, requests and downloads update content, and forwards the update data to the vehicle gateway.
3. The embedded firmware includes a bootloader and alternate application partitions.
4. The documentation describes update states for normal operation, update, data corruption, and shutdown during an update.

### Diagnostics and vehicle interaction

- The embedded application ECUs read sensors and control vehicle-related outputs.
- The ARM documentation describes temperature/fan control, direction and parking-distance checks, ultrasonic sensing, buzzer alerts, and diagnostic requests.
- The Raspberry Pi UI displays system notifications and exposes diagnostic and user interaction screens.

## Embedded firmware — ARM/

The ARM component documents a layered design:

- **MCAL:** RCC, GPIO, NVIC, EXTI, USART, CAN, SysTick, Flash programming, ADC, and DMA drivers.
- **HAL:** LED, DC motor, buzzer, temperature sensor, ultrasonic sensor, switches, fan, and communication modules.
- **Service layer:** system initialization and HEX-file parsing.
- **RTOS:** task creation, deletion, state changes, and priority-based scheduling.
- **Application layer:** main ECU, application ECUs, diagnostics, and bootloader.

Consult [ARM architecture notes](ARM/README.md) before modifying peripheral or bootloader code. Hardware register definitions, pin mappings, clock configuration, linker settings, and flash layout must match the actual target board.

## ESP32 telematics unit — NodeMCU/

The NodeMCU folder contains an Arduino sketch and C++ sources for the ESP32 telematics unit. Its README describes server communication, update-file download/decryption, diagnostics transfer, and communication with the vehicle gateway.

Open [NodeMCU documentation](NodeMCU/README.md) and the MainECU_V1 sketch in a compatible Arduino/ESP32 toolchain. Confirm the exact board package, Wi-Fi configuration, gateway protocol, and pin assignments before flashing hardware.

## Raspberry Pi interface — RPI/

The UI documentation identifies a Raspberry Pi 4 with a 5-inch touchscreen and PyQt5/Qt Designer. The Python entry point visible in the source tree is:

    RPI/GUI/Script/main.py

The documented UI modules include the main window, phone/contact screen, guide, calendar, settings, music, video, radio, and weather. Dependencies listed by the component README include PyQt5, OpenCV (cv2), and requests. Install compatible packages on the Raspberry Pi OS image used by the project.

The Images/images_rc.py and Script/images_rc.py files are Qt resource compilation outputs/utilities, not the application entry point.

See [Raspberry Pi UI documentation](RPI/README.md).

## Server and database manager — Server/

The server README describes a PyQt5 desktop tool that integrates with Firebase and encrypts data before upload using AES through PyCryptodome. Its documented dependencies include PyQt5, Pyrebase, and PyCryptodome.

See [Server documentation](Server/README.md). Firebase credentials and encryption keys must be supplied locally and must never be committed to this repository.

## Hardware and documentation

- [Hardware files](Hardware/) contains Altium schematic/library source.
- [Hardware notes](Hardware/README.md) provide the available hardware references.
- [Project documentation](Documentation/README.md) describes the supporting PDF and presentation material.
- The assets/ directory contains diagrams and screenshots referenced by the component documentation.

## Development and safety checklist

- Verify the exact MCU, ESP32 board, clock tree, pin mapping, and peripheral wiring against the hardware revision.
- Review bootloader partition boundaries and linker scripts before programming flash.
- Test update interruption, corrupted images, signature/integrity validation, rollback, and power-loss recovery on a non-production board.
- Prefer authenticated firmware images with cryptographic signature verification; encryption alone does not prove firmware authenticity.
- Do not store Wi-Fi passwords, Firebase service account files, API keys, or encryption keys in source control.
- Validate message framing, lengths, timeouts, retries, and error handling across ESP32, gateway, Raspberry Pi, and server boundaries.
- Record toolchain versions and reproducible build instructions for each firmware target.

## Verification status

This repository review improved the project overview and corrected the root-level run guidance. Firmware compilation, board flashing, Firebase integration, and end-to-end FOTA behavior have not been executed as part of this review.
