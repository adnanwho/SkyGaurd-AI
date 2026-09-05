# SkyGuard AI — Engineering Plan

## Goal

Build the MVP incrementally in dependency order.

## Implementation Order

```text
Audit
→ Configuration/Data Contracts
→ Ingestion
→ Anomaly Injection
→ Preprocessing
→ QC
→ Features
→ Isolation Forest
→ Temporal Verification
→ Spatial Verification
→ Event/Fault Classification
→ Explainability
→ Severity/Confidence
→ Sensor Health
→ Maintenance
→ Recovery
→ Pipeline
→ Dashboard
→ Evaluation
→ Hardening
```

## Phases

### Phase 0 — Audit
Inspect repository, documentation, code, tests, datasets, models, and discrepancies.

### Phase 1 — Foundation
Configuration, schemas, enums, constants, and data contracts.

### Phase 2 — Data
Historical adapter, simulator, replay, timestamp/station handling.

### Phase 3 — Injection
Spike, Frozen/Stuck, Drift/Bias, Communication/Missing with ground truth.

### Phase 4 — Preprocessing + QC
Implement all required deterministic QC rules with tests.

### Phase 5 — Features
Build ML-ready features without future leakage.

### Phase 6 — Isolation Forest
Training, persistence, loading, inference, and scoring.

### Phase 7 — Verification
Temporal and spatial verification.

### Phase 8 — Diagnosis
Evidence fusion, weather-event vs sensor-fault decision, canonical fault taxonomy.

### Phase 9 — Explanation
SHAP integration and safe unavailable state.

### Phase 10 — Operational Intelligence
Severity, confidence, sensor health, and maintenance recommendation.

### Phase 11 — Recovery
Suggested correction/data recovery while preserving raw observations.

### Phase 12 — Pipeline
Integrate all backend layers independently of the UI.

### Phase 13 — Dashboard
Streamlit/Plotly implementation following design.md and user-flow.md.

### Phase 14 — Evaluation
Clean + injected data, ground truth, actual performance metrics.

### Phase 15 — Hardening
Unit, integration, end-to-end, regression, and dashboard smoke tests.

## Priority

### P0 — MVP
Ingestion, preprocessing, QC, features, Isolation Forest, basic diagnosis, pipeline, dashboard, replay, evaluation.

### P1 — Intelligence
Temporal, spatial, event-vs-fault, SHAP, sensor health, maintenance.

### P2 — Advanced
LSTM Autoencoder, advanced temporal/seasonal modelling, richer recovery.

### P3 — Future
MQTT/Kafka, cloud, production DB, authentication, edge deployment, WIS2.0, production APIs.

## Engineering Rules

- Work one logical layer at a time.
- Test before moving forward.
- Reuse working code.
- Avoid duplicate implementations.
- Keep UI separate from core logic.
- Preserve raw data.
- Never fabricate metrics or confidence.
- Never claim unsupported functionality.

## Definition of Done

A layer is done when code, tests, stable interfaces, error handling, and documentation are verified.
