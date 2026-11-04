# SentinelX Architecture

## 1. Design goals

SentinelX is a modular, event-driven defensive platform. It must be reproducible on a developer workstation, observable, testable, and safe by construction.

Primary goals:
- process synthetic telemetry without inspecting a host;
- separate event generation, validation, detection, correlation, storage, and presentation;
- preserve explainability for every alert;
- make model evaluation reproducible;
- maintain strict network and data boundaries.

Non-goals include endpoint control, remote administration, credential collection, persistence, evasion, payload execution, and remote command dispatch.

## 2. Logical components

### 2.1 Scenario library and producer

The scenario library contains versioned JSON fixtures and deterministic generation templates. Each scenario declares its purpose, expected detection, event sequence, ATT&CK reference where applicable, and safety notes.

The Rust producer reads only these packaged fixtures and emits normalized records. It does not enumerate the filesystem, inspect process memory, query browsers, read operating-system secrets, or execute commands. A fixed seed allows an experiment to be repeated exactly.

### 2.2 Event contract

All records follow a versioned event contract. A minimal event contains:

| Field | Purpose |
|---|---|
| schema_version | Contract version |
| event_id | Unique synthetic event identifier |
| scenario_id | Source scenario |
| created_at | UTC event timestamp |
| event_type | Controlled event category |
| synthetic | Must always be true |
| entity | Fake process, host, or user reference |
| attributes | Allow-listed, non-sensitive metadata |
| provenance | Fixture name, generator version, seed |

Unknown attributes are rejected. Raw secrets, credential values, cookies, tokens, command output, and arbitrary file contents are prohibited.

### 2.3 Transport and ingestion

NATS JetStream provides local stream transport and replay. The FastAPI ingestion layer validates schema version, size limits, event category, provenance, and synthetic marker before a record can enter storage. Invalid records are quarantined as sanitized validation errors.

### 2.4 Detection workers

Detection consists of independent layers:

1. **Rule evaluator:** evaluates defensive patterns over normalized event metadata and returns rule ID, matched fields, explanation, and severity.
2. **Anomaly evaluator:** computes feature vectors from synthetic event metadata and scores deviations from a documented baseline.
3. **Correlation worker:** combines evidence within bounded windows and produces an incident candidate.

The engine preserves individual evidence contributions. A model score alone must never become an unexplained high-impact action.

### 2.5 Persistence

- **ClickHouse:** append-oriented event history and analytical queries.
- **PostgreSQL:** accounts, roles, cases, alert state, configuration, and audit records.
- **Neo4j:** relationships among synthetic entities, event IDs, rules, indicators, and cases.

Each store has a separate least-privilege service identity. Retention and deletion policies are documented before data is generated.

### 2.6 Analyst console

The Next.js console consumes the API rather than connecting directly to databases or message brokers. It provides:
- incident queue with severity and confidence;
- event explorer and filters;
- incident evidence and timeline;
- rule/model explanation;
- synthetic scenario playback controls;
- case notes and audit history;
- evaluation results and export.

Playback can only ask the scenario service to emit a pre-authored fixture. It cannot issue commands to an endpoint.

## 3. Event lifecycle

~~~mermaid
sequenceDiagram
    participant Analyst
    participant UI as Analyst Console
    participant API as FastAPI
    participant Producer as Scenario Producer
    participant Bus as NATS
    participant Detector
    participant Stores as Data Stores

    Analyst->>UI: Select a synthetic scenario
    UI->>API: Request scenario replay
    API->>Producer: Request approved fixture ID
    Producer->>Bus: Publish synthetic events
    Bus->>API: Deliver validated event
    API->>API: Validate schema and synthetic marker
    API->>Detector: Submit normalized event
    Detector->>Detector: Evaluate rules and anomaly model
    Detector->>Stores: Persist evidence and incident candidate
    UI->>API: Query incident and event timeline
    API-->>UI: Return sanitized evidence
~~~

## 4. Trust boundaries

- **Browser to API:** authenticated requests, CSRF protection where cookie sessions are used, strict CORS, rate limits, and input validation.
- **API to broker:** service identity, bounded message size, allow-listed subjects, and no arbitrary publish endpoint exposed to the browser.
- **Workers to stores:** least-privilege credentials and parameterized queries.
- **Scenario producer:** read-only access to scenario fixtures and publish-only access to its dedicated local subject.
- **External network:** not required for simulation. Default-deny egress is preferred.

## 5. Reliability and scalability

Workers should be idempotent using event IDs. Retries must not duplicate incidents. Dead-letter records contain only sanitized metadata. Backpressure, stream retention, bounded queues, and replay limits must be configurable. Load tests should report throughput and p95/p99 processing latency.

## 6. Observability

OpenTelemetry traces should connect scenario ID, event ID, detection evaluation, correlation, and API response. Prometheus metrics should include ingestion rate, rejected-event count, processing latency, consumer lag, alert count, and model scoring duration. Logs must not contain secrets or arbitrary payload contents.

## 7. Deployment profiles

- **Developer:** local Docker Compose; synthetic fixtures; loopback-only ports.
- **Evaluation:** repeatable dataset manifests and fixed seeds; metrics exported for analysis.
- **Demonstration:** preloaded incidents and controlled replay; no real endpoint sensor.

Kubernetes/k3d can be an optional deployment exercise after the local architecture is tested. It is not required for the core academic result.
