# SkyGuard AI — User Flow

## Primary Operator Flow

```text
Open Dashboard
→ Select Station
→ View Temperature / Pressure / Humidity
→ Review Station Status
→ Anomaly Detected?
→ Open Alert
→ Review QC + ML Evidence
→ Temporal Verification
→ Spatial Verification
→ Weather Event vs Sensor Fault
→ Root Cause
→ Severity + Confidence
→ Sensor Health
→ Maintenance Recommendation
→ Suggested Correction / Data Recovery
```

## Anomaly Investigation

The operator should be able to inspect the station, timestamp, affected variable, observed value, anomaly evidence, QC evidence, temporal behavior, spatial behavior, event/fault decision, fault type, severity, confidence, explanation, sensor health, recommendation, and recovery suggestion.

## Weather Event vs Sensor Fault

The system combines physics/QC, Isolation Forest, temporal, and spatial evidence.

Example:
- Station A = 55°C
- Neighbors ≈ 31°C
- Result: evidence of an isolated sensor anomaly.

Contrasting example:
- Station A = 42°C
- Station B = 41.5°C
- Station C = 42.3°C
- Result: possible regional weather event.

Insufficient evidence must produce an explicit uncertain/unavailable state.

## Replay Flow

```text
Select Dataset → Select Station → Start Replay
→ Sequential Observations → Detection → Alert
→ Evidence → Diagnosis → Recommendation
```

## Recovery Flow

```text
Confirmed Anomaly
→ Generate Suggestion
→ Show Original Value
→ Show Proposed Value
→ Show Method + Evidence
→ Operator Review
```

Raw observations must remain immutable.

## Canonical Fault Types

- Spike
- Frozen/Stuck
- Drift/Bias
- Communication/Missing
