# SkyGuard AI — Technical Design Document (TDD)

## Purpose

Define the technical design for the modular SkyGuard AI MVP.

## Canonical Architecture

```text
AWS Observation
→ Schema Validation
→ Preprocessing
→ Physics / Rule QC
→ Feature Engineering
→ Isolation Forest
→ Temporal Verification
→ Spatial Verification
→ Evidence Fusion
→ Weather Event / Sensor Fault
→ SHAP Explanation
→ Root Cause
→ Severity + Confidence
→ Sensor Health
→ Maintenance Recommendation
→ Suggested Correction / Data Recovery
→ Streamlit Dashboard
```

## Module Boundaries

Suggested modules:

```text
src/
├── config.py
├── schemas.py
├── data_simulator.py
├── historical_adapter.py
├── anomaly_injector.py
├── preprocessing.py
├── feature_engineering.py
├── rule_checks.py
├── isolation_forest_model.py
├── spatial_consistency.py
├── lstm_autoencoder.py
├── event_classifier.py
├── explainability.py
├── scoring.py
├── sensor_health.py
├── maintenance.py
└── pipeline.py

dashboard/
└── app.py
```

Reuse equivalent existing modules instead of duplicating them.

## Data Contract

Pipeline output should retain, where applicable:
- validated observation
- QC evidence
- model evidence
- temporal evidence
- spatial evidence
- event/fault classification
- fault type
- explanation
- severity
- confidence
- sensor health
- recommendation
- recovery suggestion

## Data Integrity

Raw observations are immutable. Proposed corrections are separate records.

## ML

Isolation Forest is the primary MVP multivariate detector.

LSTM Autoencoder is advanced/optional unless already implemented and validated.

## Evidence Fusion

Diagnosis combines QC + ML + temporal + spatial evidence. A single signal should not automatically override the full evidence context.

## Explainability

SHAP may attribute model output to features. It is not causal proof.

## Health

MVP health is a transparent operational score/trend, not a predictive-maintenance claim.

## Recovery

Recovery contains original value, proposed value, method, confidence, and reason. It does not silently modify source data.

## Error Handling

Handle invalid input, insufficient history, missing spatial context, unavailable models, unavailable explanations, and invalid configuration.

## Technical Acceptance

The pipeline must be independently callable from the dashboard, modules must be testable, contracts must be consistent, and the end-to-end workflow must work with controlled anomalies.
