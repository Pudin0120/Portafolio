# Module Prototype Development Notes

This folder preserves a short set of early WebSocket/Android integration notes from the smart-home prototype.

The original note references:
- Eclipse and JDK 7.
- Android 4.4.2.
- Tomcat 8.
- Android internet permission and the Autobahn Android WebSocket library.
- JSR-356 WebSocket API references.
- JSON message parsing examples.

These notes are historical and incomplete; they are not a standalone application or a reproducible build.

## Modernization guidance

- Use a maintained Android SDK and a supported JDK/Android Gradle Plugin.
- Use secure WebSocket connections (WSS) with authenticated sessions.
- Validate and version message payloads; do not parse untrusted JSON without schema/field validation.
- Document reconnect behavior, timeouts, message size limits, and error handling.
- Keep server credentials and device secrets outside source control.

For the wider architecture and the separate Android client modules, see the [parent project overview](../README.md) and [Android prototype notes](../technical-solutions/1_2-android-music-player-implementation/README.md).
