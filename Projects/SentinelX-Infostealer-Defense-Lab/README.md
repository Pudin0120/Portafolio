# SentinelX — Infostealer Detection & Threat Emulation Lab

> **Academic cybersecurity project · Defensive research only · Synthetic telemetry**

SentinelX is a controlled security research platform for studying infostealer-like behavior from the defender's perspective. It generates harmless, pre-defined endpoint and network event records, streams them into a detection pipeline, correlates alerts, and presents an auditable incident timeline.

It is **not** a stealer, remote access tool, botnet, or command-and-control framework. It does not collect credentials, cookies, tokens, browser data, or personal files. It does not execute attack payloads, establish persistence, hide processes, disable security controls, or open outbound connections to simulated command servers.

The project uses publicly described threat behaviors, including those associated with Lumma Stealer, only as high-level research context. All exercises are represented as synthetic JSON telemetry and metadata.

## Academic objective

Design, implement, and evaluate a hybrid detection platform that combines:

1. deterministic, explainable behavior rules;
2. statistical anomaly detection over synthetic event streams;
3. event correlation and incident scoring;
4. threat-intelligence relationships and ATT&CK technique references;
5. reproducible experiments with measurable false-positive and detection rates.

**Research question:** Does a hybrid rule-based and anomaly-detection approach improve detection quality and investigation context over either method alone when evaluated against a reproducible synthetic infostealer-behavior dataset?

## Proposed technology stack

| Layer | Proposed technology | Responsibility |
|---|---|---|
| Web console | Next.js, React, TypeScript | Analyst dashboard, event explorer, case management |
| API | Python, FastAPI, Pydantic | Typed REST API, validation, authentication, orchestration |
| Safe event producer | Rust | Emits only pre-authored synthetic telemetry fixtures |
| Event transport | NATS JetStream | Local event streaming, replay, consumer groups |
| Event analytics | ClickHouse | High-volume event storage and analytical queries |
| Relational data | PostgreSQL | Users, cases, rules, experiment metadata, audit records |
| Intelligence graph | Neo4j | Relationships between synthetic indicators, events, rules, and cases |
| Detection | Sigma-compatible rules, scikit-learn, River | Explainable matching and streaming anomaly scoring |
| Model governance | MLflow | Experiment tracking, model/version lineage, metrics |
| Observability | OpenTelemetry, Prometheus, Grafana, Loki | Traces, metrics, dashboards, structured logs |
| Delivery and security | Docker Compose, GitHub Actions, Semgrep, Trivy | Reproducible local environment and secure CI checks |

Versions will be pinned to mutually compatible stable releases during implementation and recorded in lockfiles/container tags. The proposal intentionally avoids floating production dependencies.

## Core capabilities

- **Scenario simulator:** selects a documented scenario and emits fixed, synthetic events. It never performs the represented host action.
- **Event ingestion:** validates schemas, timestamps, source identity, scenario identifiers, and event integrity.
- **Detection engine:** evaluates transparent rules and anomaly models independently, then combines their evidence.
- **Correlation engine:** groups related events into incidents using time windows, entity references, and explainable scoring.
- **Threat-intelligence graph:** links synthetic indicators and behaviors to detections, cases, and public ATT&CK references.
- **Analyst workbench:** filters events, inspects evidence, acknowledges alerts, and documents an investigation.
- **Forensic timeline:** reconstructs the sequence of generated events with a full audit trail.
- **Experiment laboratory:** compares rules-only, anomaly-only, and hybrid approaches using fixed datasets and repeatable seeds.
- **Report generation:** exports sanitized case summaries and experiment results.

## Safe simulation scenarios

The simulator produces records such as:

- a **metadata-only credential-store access attempt** (no store is opened or read);
- an unusual process relationship represented as a fixture (no process is spawned);
- a persistence-related configuration change represented as an event (no registry, startup folder, service, or scheduled task is modified);
- an unusual outbound-flow record (no socket is opened and no data is transmitted);
- an unexpected archive or staging event represented by synthetic metadata (no user files are collected or archived);
- a suspicious execution-chain sequence represented by a prerecorded event list (no payload is executed).

Every event is marked as synthetic and includes a scenario ID, event ID, timestamp, and provenance metadata.

## Architecture overview

~~~mermaid
flowchart LR
    A[Scenario Library] --> B[Safe Rust Event Producer]
    B --> C[NATS JetStream]
    C --> D[FastAPI Ingestion]
    D --> E[Schema Validation]
    E --> F[Detection Workers]
    F --> G[Rule Engine]
    F --> H[Anomaly Models]
    G --> I[Correlation Engine]
    H --> I
    I --> J[(ClickHouse Events)]
    I --> K[(PostgreSQL Cases)]
    I --> L[(Neo4j Intelligence Graph)]
    J --> M[Analyst API]
    K --> M
    L --> M
    M --> N[Next.js Analyst Console]
    F --> O[OpenTelemetry]
    O --> P[Prometheus / Grafana / Loki]
~~~

See [Architecture](docs/ARCHITECTURE.md), [Threat Model](docs/THREAT-MODEL.md), [Research Plan](docs/RESEARCH-PLAN.md), and [Safety Boundaries](docs/SAFETY-BOUNDARIES.md).

## Suggested repository layout

~~~text
SentinelX-Infostealer-Defense-Lab/
├── apps/
│   ├── analyst-console/       # Next.js + TypeScript
│   └── api/                   # FastAPI application
├── services/
│   ├── scenario-producer/     # Rust synthetic-event generator
│   ├── detection-worker/      # Rules and anomaly scoring
│   └── correlation-worker/    # Incident grouping and scoring
├── packages/
│   ├── event-contracts/       # Versioned schemas and fixtures
│   └── detection-rules/       # Defensive, explainable rules
├── datasets/
│   ├── synthetic/             # Generated, non-sensitive datasets
│   └── manifests/             # Checksums, labels, generation seeds
├── infra/
│   ├── compose/               # Local-only infrastructure
│   └── observability/         # Dashboards and collector config
├── experiments/               # Reproducible evaluation scripts
├── docs/
└── tests/
~~~

## Evaluation

The academic evaluation will report precision, recall, F1-score, false-positive rate, per-scenario detection latency, event throughput, and resource consumption. Each experiment will publish its dataset manifest, random seed, configuration, and software versions. A held-out synthetic test set will reduce overfitting.

## Security and privacy principles

- Synthetic fixtures only; no real credentials, secrets, browser profiles, session stores, or personal files.
- No malware samples or executable payloads are required.
- No persistence, stealth, evasion, privilege escalation, process injection, or security-control tampering.
- No command-and-control listener, remote tasking, or exfiltration channel.
- No outbound network traffic is required for scenario execution.
- Local services bind to loopback by default; deployment guidance will require explicit review before exposing anything.
- Dataset fixtures contain fake values and are scanned for accidental secrets.
- Every simulated event retains provenance and is auditable.

## Development status

**Current state: project proposal and architecture baseline.** The repository branch contains the initial project brief and design documents. Runtime services, user interface, detection rules, tests, and experiments must be implemented and validated in subsequent milestones. The presence of a proposed technology in this document does not mean that component is already implemented.

## Planned milestones

1. **Foundation:** contracts, synthetic scenario catalogue, data generator, repository quality gates.
2. **Ingestion:** FastAPI, NATS, schema validation, ClickHouse/PostgreSQL persistence.
3. **Detection:** explainable rules, anomaly baselines, correlation and scoring.
4. **Analyst console:** cases, event search, evidence views, timeline and audit history.
5. **Threat intelligence:** Neo4j graph, curated public references, ATT&CK mapping.
6. **Evaluation:** reproducible datasets, benchmark protocol, model comparison and report.
7. **Hardening:** threat-model review, SBOM, dependency scanning, load tests and reproducible deployment.

## License and use

This project is intended for supervised academic research, defensive security engineering, and controlled demonstrations. Use only the included synthetic dataset and local lab environment.
