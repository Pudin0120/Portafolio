# SentinelX Threat Model

## 1. Scope

This threat model covers the SentinelX defensive research platform and its synthetic scenario environment. It does not authorize testing against third-party systems or the creation of functional malware.

## 2. Assets

- synthetic event fixtures and dataset manifests;
- detection rules and model artifacts;
- analyst accounts, roles, and case notes;
- incident evidence and audit history;
- database and broker credentials used by the local lab;
- software supply-chain metadata and build artifacts.

## 3. Trust boundaries

1. Analyst browser to API.
2. API to event broker.
3. Scenario producer to event broker.
4. Detection workers to analytical and relational stores.
5. Build pipeline to container images and dependency artifacts.

The scenario producer is deliberately isolated from host telemetry and has no endpoint-control interface.

## 4. Adversaries and misuse cases

| Threat | Potential impact | Mitigation |
|---|---|---|
| Malicious or malformed event fixture | Parser abuse, resource exhaustion, misleading alerts | Strict schema, size/depth limits, allow-listed fields, fuzz tests |
| Forged event provenance | False incident attribution | Signed dataset manifests, producer identity, deterministic IDs |
| Unauthorized analyst access | Disclosure or alteration of cases | RBAC, short-lived sessions, audit log, least privilege |
| Broker subject abuse | Unauthorized event injection | Dedicated subjects, service credentials, broker ACLs |
| Compromised dependency | Supply-chain compromise | Lockfiles, SBOM, Semgrep, Trivy, dependency review |
| Model poisoning through altered fixtures | Incorrect anomaly scores | Versioned datasets, checksums, separated train/test manifests |
| Secret accidentally committed | Credential exposure | Secret scanning, fake-only examples, rotation procedure |
| Accidental external network exposure | Lab misuse or data leakage | Loopback binding, default-deny egress, deployment review |

## 5. Abuse-case controls

- The generator cannot accept arbitrary shell commands or executable paths.
- Scenario IDs resolve only to fixtures committed in the approved catalogue.
- Event attributes are typed and allow-listed; arbitrary blobs are not accepted.
- No code path reads browser stores, password vaults, cookies, tokens, environment secrets, or user documents.
- No code path modifies startup configuration, services, scheduled tasks, registry entries, security settings, or firewall rules.
- No remote tasking protocol or C2 listener exists.
- No simulated network event opens a socket or transmits data.
- Model outputs are advisory and cannot trigger endpoint actions.
- Exported reports are sanitized and contain synthetic identifiers only.

## 6. Security testing

Required tests include schema-validation tests, property-based tests for event parsing, API authorization tests, broker ACL tests, SQL-injection tests, dependency and container scans, secret scans, and negative tests confirming that prohibited host and network capabilities are absent.

## 7. Residual risks

Even a synthetic lab can be misconfigured, exposed, or supplied with real data by mistake. Documentation, CI checks, default-deny networking, local-only bindings, and repeated review reduce but do not eliminate this risk. The project should be demonstrated with a clean local environment and generated fixtures only.
