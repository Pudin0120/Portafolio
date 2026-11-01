# WebSocket and WebRTC Research

This folder preserves the original topic marker for real-time communication research. No WebSocket server, WebRTC signaling implementation, client source, dependency manifest, or build descriptor is present here.

## Suggested architecture

- Use WebSocket Secure (WSS) for authenticated, bidirectional application signaling.
- Use WebRTC for peer-to-peer media/data only when the use case requires it.
- Use an explicit signaling protocol with message types, versioning, correlation IDs, and payload validation.
- Authenticate each connection and authorize every device/action message.
- Define reconnect, heartbeat, timeout, maximum message size, and rate-limit behavior.
- Do not place device keys or API secrets in browser/mobile source code.

## Current status

This directory is a research placeholder rather than a runnable component. The wider archive contains early Android/WebSocket notes in [module-prototype-development](../../module-prototype-development/README.md).
