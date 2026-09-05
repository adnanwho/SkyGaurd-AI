# SkyGuard AI — Testing Strategy

## Principles

- Test each layer before depending on it.
- Test normal data as well as anomalies.
- Use controlled anomaly injection with ground truth.
- Never fabricate evaluation metrics.
- Preserve raw observations.
- Test uncertainty and unavailable context.
- Separate model training tests from inference tests.

## Unit Tests

### Data
Valid observations, missing fields, invalid types, timestamps, duplicates, station IDs.

### QC
Physical range, rate/step, persistence, missingness, dew-point/thermodynamic consistency, cross-variable checks.

### Features
Deltas, rolling features, temporal features, insufficient history, no future leakage.

### Injection
Spike, Frozen/Stuck, Drift/Bias, Communication/Missing, with ground truth.

### ML
Training, persistence, loading, inference, reproducibility, malformed input, unavailable model.

### Verification
Temporal spike/frozen/drift/normal cases and spatial isolated-event/regional-event/missing-neighbor cases.

### Diagnosis
Normal, possible weather event, uncertain, and all canonical fault types.

### Explainability
Available/unavailable SHAP explanation and correct feature alignment.

### Health
Healthy, occasional anomalies, repeated anomalies, missingness, drift.

### Recovery
Original value remains unchanged; proposed value, method, reason, and confidence are stored separately.

## Integration Test

```text
Input
→ Schema
→ Preprocessing
→ QC
→ Features
→ Isolation Forest
→ Verification
→ Classification
→ Explanation
→ Severity/Confidence
→ Health
→ Recommendation
→ Output
```

## End-to-End Scenarios

1. Normal data
2. Temperature spike
3. Frozen sensor
4. Drift
5. Communication failure
6. Regional weather event
7. Isolated sensor fault

## Evaluation

Use clean data + controlled injection + ground truth. Calculate actual precision, recall, F1, false positives, false negatives, detection latency, root-cause performance, and event-vs-fault performance.

## Definition of Done

A layer is complete only when implementation, tests, error handling, stable output contracts, and documentation are all present and verified.
