# SkyGuard AI — Evaluation Specification

## Goal

Measure anomaly detection, fault diagnosis, weather-event discrimination and processing performance using reproducible ground truth.

## Dataset

```text
Clean observations
+
Controlled anomaly injection
+
Known ground truth
```

Each injected scenario should record:
`scenario_id`, `station_id`, `timestamp/window`, `fault_type`, `affected_parameter`, `expected_event_type`.

## Required scenarios

1. Normal baseline
2. Spike
3. Frozen/Stuck
4. Drift/Bias
5. Communication/Missing
6. Multivariate inconsistency
7. Isolated station fault
8. Regional weather event
9. Seasonal extreme
10. Repeated faults / declining health

## Detection metrics

Precision:
`TP / (TP + FP)`

Recall:
`TP / (TP + FN)`

F1:
`2 × Precision × Recall / (Precision + Recall)`

Also:
- False-positive rate
- False-negative rate

## Root-cause evaluation

Report per-class precision, recall, F1 and confusion matrix for:
`Spike`, `Frozen/Stuck`, `Drift/Bias`, `Communication/Missing`.

## Event-vs-fault evaluation

Evaluate regional weather-event recognition separately from isolated sensor-fault recognition.

## Latency

Measure actual:
- QC latency
- ML latency
- contextual latency
- explanation latency
- total pipeline latency

Report mean/median/p95 only when enough measurements exist.

## Protocol

1. Freeze test dataset.
2. Freeze model/configuration.
3. Run pipeline.
4. Store predictions.
5. Compare to ground truth.
6. Calculate metrics.
7. Store run metadata.
8. Generate report.

Do not tune against the final test set after viewing results without recording a new experiment.

## Robustness

Test missing values, duplicates, irregular intervals, multiple violations, missing neighbors, no spatial data, ML unavailable and legitimate extremes.

## Rule

No performance number may appear in the PPT/dashboard as a project result unless produced by a reproducible evaluation run.
