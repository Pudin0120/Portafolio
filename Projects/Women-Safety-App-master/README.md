# Women Safety App — Android Prototype

An experimental Android application for storing up to two trusted contacts and a reference phone number. The source also contains an older accelerometer and location-service experiment, but the emergency-alert workflow is **not complete**.

> **Safety notice:** This is an academic prototype, not a dependable personal-safety or emergency-response product. It does not currently send SMS alerts, call emergency services, or guarantee background shake detection. Do not rely on it during an emergency.

## Technology stack

| Component | Version / detail |
| --- | --- |
| Language | Java 8 |
| Android Gradle Plugin | 7.4.2 |
| Gradle | 7.5 |
| Compile SDK | 33 |
| Minimum SDK | 19 |
| Target SDK | 22 (legacy compatibility only) |
| Local persistence | Android SQLite |
| Support library | Android Support v4 19.1.0 |

## Requirements

- JDK 11
- Android SDK Platform 33
- Gradle 7.5
- Android emulator or device for manual testing

The Gradle wrapper scripts are present, but gradle-wrapper.jar is not included. Install Gradle 7.5 or use Android Studio's configured Gradle installation.

## Build

From this directory:

    gradle --version
    gradle --no-daemon :app:assembleDebug

The debug APK is generated at:

    app/build/outputs/apk/debug/app-debug.apk

The repository's GitHub Actions workflow also runs this build with Gradle 7.5 and Java 11.

## Current functionality

- Register up to two trusted contacts.
- Register a reference phone number.
- Display locally stored contact details.
- Retain the original experimental accelerometer, GPS, and reverse-geocoding source files for study.

## Improvements in this revision

- Replaced the invalid Android Gradle plugin version and removed the retired JCenter repository.
- Moved the build to a reproducible Gradle 7.5 / Android Gradle Plugin 7.4.2 configuration.
- Added an Android namespace and explicit exported settings for application components.
- Disabled Android application backup for locally stored contact data.
- Removed unused SMS and phone-state permissions because no SMS sending implementation is active.
- Added phone-number and contact-name validation.
- Replaced SQL string concatenation with ContentValues-based SQLite inserts.
- Enforced the documented two-contact limit by replacing the oldest saved contact.
- Closed database cursors and connections reliably.
- Prevented opening the contact list from unexpectedly starting background sensor monitoring.
- Rewrote the in-app instructions so they do not falsely promise emergency SMS alerts.

## Important limitations before any real-world use

- The SMS-sending code in the original service is commented out. No emergency message is delivered.
- The accelerometer service is an unfinished experiment and is not connected to the main screen as an explicit, user-controlled safety mode.
- The target SDK is intentionally kept at 22 to preserve the old permission model while the project is being stabilized. This is not suitable for a modern Google Play release.
- Before raising target SDK, implement and test runtime permission flows, foreground-service behavior, notification controls, and Android background-execution requirements.
- Do not collect, transmit, or store location data until the user has clearly opted in and the data handling is documented.
- Add automated tests for contact validation, storage limits, and database migration.
- Replace the legacy Support Library with AndroidX in a dedicated migration.

## Author

Joseff Antonio Laverde Avendaño
