# SkyGuard AI — Design Brief

## Product

SkyGuard AI is an operator-first intelligent anomaly detection and sensor-health system for Automatic Weather Stations.

## Design Goal

Help an operator answer:

> What happened, why does the system think it happened, how confident is the diagnosis, and what should I do next?

## Experience Principles

The interface should be:
- clear
- technical
- trustworthy
- evidence-driven
- operational
- honest about uncertainty

## Information Priority

1. Active critical anomaly
2. Station status
3. Affected variable/value
4. Weather-event vs sensor-fault decision
5. Severity/confidence
6. Evidence
7. Root cause
8. Recommended action
9. Sensor health
10. Historical context

## Dashboard Structure

```text
Header / Station Selector
        ↓
Temperature | Pressure | Humidity | Health
        ↓
Live / Historical Charts
        ↓
Alerts + Anomaly Table
        ↓
Selected Anomaly
        ↓
Evidence → Diagnosis → Explanation → Recommendation
```

## Anomaly Detail

Show station, timestamp, variable, observed value, anomaly status/score, failed QC rules, temporal evidence, spatial evidence, event/fault result, root cause, severity, confidence, SHAP attribution when available, sensor health, maintenance recommendation, and suggested correction.

## Trust

Clearly distinguish observed facts, rule evidence, model outputs, inferred diagnosis, and recommendations.

SHAP is feature attribution, not causal proof.

## Recovery UX

Always show:
- original value
- proposed value
- method
- evidence/confidence
- operator review state

Never imply that raw data was silently replaced.

## Acceptance

An operator should be able to go from:

**station → anomaly → evidence → diagnosis → action**

without inspecting source code.
