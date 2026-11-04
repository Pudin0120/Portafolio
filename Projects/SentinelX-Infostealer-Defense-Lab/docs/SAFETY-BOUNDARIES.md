# SentinelX Safety Boundaries

These requirements are mandatory acceptance criteria for every component, test, demonstration, and future contribution.

## Allowed

- Generate synthetic JSON event records from reviewed, version-controlled fixtures.
- Replay prerecorded event sequences with deterministic seeds.
- Analyze metadata included in those fixtures.
- Map simulated behavior categories to public defensive frameworks.
- Evaluate defensive rules and statistical models.
- Display sanitized incident timelines and reports.
- Run local infrastructure for the isolated academic lab.

## Prohibited

- Reading, harvesting, encrypting, or transmitting real credentials, cookies, tokens, browser profiles, password stores, wallets, or personal files.
- Building or integrating credential theft, keylogging, screen capture, clipboard collection, browser injection, or session hijacking.
- Implementing persistence, stealth, anti-analysis, sandbox evasion, process injection, privilege escalation, or security-tool disabling.
- Downloading, executing, packing, or deploying malware payloads.
- Creating command-and-control channels, remote tasking, bot management, or data-exfiltration functions.
- Scanning, exploiting, or testing systems without explicit authorization.
- Using real personal or organizational telemetry in the default dataset.

## Implementation controls

1. The scenario producer reads only its fixture directory and has no endpoint sensor permissions.
2. Scenario execution never starts a process or performs a host modification.
3. Network-behavior scenarios are represented as records; they do not create network connections.
4. Ingestion rejects events where the synthetic marker is not true.
5. Fixtures are checked for secrets and personal data in CI.
6. Local services bind to loopback by default.
7. Model output is advisory and cannot execute actions.
8. Every event and incident maintains source provenance.

## Pull request checklist

- [ ] The change uses synthetic records only.
- [ ] It does not inspect host secrets, browser stores, or personal files.
- [ ] It does not execute commands or payloads.
- [ ] It does not establish persistence or modify security settings.
- [ ] It does not add remote tasking, stealth, evasion, or exfiltration.
- [ ] New event fields are documented and allow-listed.
- [ ] Tests include negative cases for unsafe input.
- [ ] Dependencies are pinned and reviewed.
- [ ] Documentation accurately describes what is implemented.

A change that violates any prohibited boundary must not be merged.
