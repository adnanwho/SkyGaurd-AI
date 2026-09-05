# SkyGuard AI — Implementation Plan

## Build order

```text
Phase 0 → Project Setup
Phase 1 → Data Foundation
Phase 2 → Detection Core
Phase 3 → Contextual Intelligence
Phase 4 → Explainability + Health
Phase 5 → Dashboard + Replay
Phase 6 → Evaluation + QA
Phase 7 → Advanced Modules
Phase 8 → Packaging
```

## Phase 0 — Setup
- Repository structure
- Python environment
- Requirements
- Configuration
- Schemas
- Logging
- Pytest

**Exit:** clean environment installs and tests execute.

## Phase 1 — Data
- Synthetic AWS simulator
- CSV/Parquet loader
- Anomaly injector
- Deterministic seeds
- Multi-station data
- Ground-truth labels

Scenarios: normal, spike, frozen/stuck, drift/bias, communication/missing, regional event, isolated fault.

## Phase 2 — Detection Core
- Preprocessing
- Range, step/rate, persistence and thermodynamic QC
- Feature engineering
- Isolation Forest
- Joblib persistence
- Basic classification

## Phase 3 — Intelligence
- Neighbor association
- Spatial deviation/consensus
- Temporal evidence
- Event-vs-fault logic
- Severity
- Confidence
- Standard fault taxonomy

## Phase 4 — XAI + Health
- SHAP
- Plain-English explanations
- Rolling health score
- Degradation trend
- Maintenance recommendations

## Phase 5 — Product
- Streamlit shell
- Metric cards
- Plotly charts
- Anomaly table/detail
- Evidence panel
- Spatial panel
- Health/maintenance panels
- Replay controls

## Phase 6 — Evaluation
- Ground-truth runner
- Precision/Recall/F1
- False positives/negatives
- Root-cause metrics
- Latency
- Regression tests
- Evaluation report

## Phase 7 — Advanced
Only after the core is stable:
- LSTM Autoencoder
- Advanced temporal analysis
- Suggested correction/reconstruction

## Phase 8 — Packaging
- README
- requirements
- examples
- tests
- evaluation report
- architecture consistency review
- PPT/demo consistency review

## Priorities

**P0:** data schema, simulator, injector, preprocessing, QC, Isolation Forest, classification, evaluation, dashboard, replay, tests.

**P1:** spatial validation, SHAP, severity/confidence, health, maintenance.

**P2:** LSTM Autoencoder, suggested recovery.

**P3:** MQTT/Kafka, WIS2.0, cloud, authentication, ESP32/edge.

## Coding-agent rules
Read `prd.md`, `architecture.md`, `data-schema.md` and the relevant technical specification before implementation. Inspect existing code first, add tests with new behavior, preserve source observations, do not fabricate metrics, and do not reintroduce the discarded 3-agent/18B/70B+ architecture.
