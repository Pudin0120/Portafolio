# SentinelX Academic Research Plan

## 1. Proposed title

**Design and Evaluation of a Hybrid Detection Platform for Infostealer-Like Behavior Using Synthetic Endpoint Telemetry**

## 2. Problem statement

Infostealer incidents may involve several weak signals distributed across endpoint and network telemetry. Single-event rules can miss sequences, while anomaly models can produce findings that are difficult to explain. A defensive platform should correlate explainable rules and statistical deviations while preserving evidence and controlling false positives.

This project investigates the detection problem using synthetic telemetry only. It does not collect real credentials or reproduce malware execution.

## 3. General objective

Design, implement, and evaluate a modular platform that detects and explains synthetic infostealer-like behavior through rule-based analysis, anomaly scoring, and event correlation.

## 4. Specific objectives

1. Define a versioned event schema and a reproducible synthetic scenario catalogue.
2. Implement a safe event pipeline with validation, storage, and replay.
3. Create an explainable rule evaluator for selected behavior categories.
4. Build and document an anomaly-detection baseline.
5. Correlate detections into incident timelines with evidence provenance.
6. Provide an analyst interface for review, classification, and reporting.
7. Compare rule-only, anomaly-only, and hybrid approaches using a held-out dataset.

## 5. Hypotheses

- **H1:** The hybrid approach will improve recall over rules alone on the held-out synthetic scenarios.
- **H2:** The hybrid approach will preserve a lower false-positive rate than anomaly-only scoring at a comparable recall target.
- **H3:** Event correlation will reduce duplicate alerts and improve investigation context.

These are hypotheses to test, not promised outcomes.

## 6. Experimental groups

| Group | Configuration |
|---|---|
| A — Rules | Deterministic rules only |
| B — Anomaly | Statistical anomaly model only |
| C — Hybrid | Rules, anomaly evidence, and correlation |

All groups receive the same dataset versions and event ordering. Hyperparameters are selected using training/validation data, never the held-out test set.

## 7. Dataset design

The dataset contains fully synthetic records with:
- scenario class and expected label;
- deterministic generation seed;
- event sequence and time offsets;
- benign background activity;
- controlled noise and duplicate events;
- manifest, schema version, and cryptographic checksum.

The dataset must not contain real usernames, email addresses, credentials, access tokens, cookies, browser data, personal file contents, or captured traffic.

## 8. Metrics

- **Precision:** proportion of positive detections that are correct.
- **Recall:** proportion of positive scenarios detected.
- **F1-score:** harmonic mean of precision and recall.
- **False-positive rate:** proportion of benign samples incorrectly flagged.
- **Detection latency:** time from the first relevant generated event to an incident candidate.
- **Throughput:** validated events processed per second.
- **Resource cost:** CPU, memory, storage, and model inference time.

Results should include confidence intervals where sample size permits. Per-scenario results must be reported to expose class imbalance and blind spots.

## 9. Reproducibility requirements

Every experiment records:
- code commit and release identifier;
- dependency lockfiles and container image tags;
- dataset manifest and checksum;
- random seed;
- ruleset and model versions;
- configuration and evaluation script;
- metrics in machine-readable form.

A clean checkout must be able to reproduce the published tables and plots.

## 10. Limitations

Synthetic telemetry is useful for repeatability and safety but cannot fully represent endpoint diversity, operating-system noise, adversarial adaptation, or real incident conditions. Results must not be presented as proof of production-grade malware detection. Any future evaluation with real-world telemetry requires separate ethics, privacy, legal, and institutional approval.

## 11. Expected academic deliverables

- requirements specification and system architecture;
- threat model and safety analysis;
- implemented source code and automated tests;
- synthetic dataset and data dictionary;
- experiment protocol and results;
- limitations and future work;
- final thesis report and live demonstration.
