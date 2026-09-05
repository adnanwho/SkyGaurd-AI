# SkyGuard AI — Data Schema

## Raw observation

Required:

| Field | Type | Description |
|---|---|---|
| `station_id` | string | Station identifier |
| `timestamp` | datetime | Observation time |
| `temperature` | float/null | Air temperature °C |
| `pressure` | float/null | Atmospheric pressure hPa |
| `humidity` | float/null | Relative humidity % |

Optional:
`latitude`, `longitude`, `elevation`.

## CSV example

```csv
station_id,timestamp,temperature,pressure,humidity
AWS-01,2026-01-01T12:00:00,31.4,1008.2,61.0
AWS-01,2026-01-01T12:01:00,31.5,1008.1,60.8
AWS-02,2026-01-01T12:00:00,31.1,1008.5,62.0
```

## Processed record

```text
station_id
timestamp
observation
quality
features
anomaly
context
diagnosis
explanation
health
maintenance
recovery
```

Suggested nested fields:

```text
anomaly: is_anomaly, score
context: event_type, temporal_evidence, spatial_evidence
diagnosis: root_cause, severity, confidence
health: health_score, health_status, health_trend
recovery: original_value, suggested_value, status
```

## Enumerations

Event type:
`NORMAL | SENSOR_FAULT | WEATHER_EVENT | UNCERTAIN`

Root cause:
`NONE | SPIKE | FROZEN_STUCK | DRIFT_BIAS | COMMUNICATION_MISSING | UNKNOWN`

Severity:
`LOW | MEDIUM | HIGH | UNKNOWN`

Health:
`HEALTHY | WARNING | DEGRADING | CRITICAL | UNKNOWN`

Recovery:
`NOT_AVAILABLE | NOT_REQUIRED | SUGGESTED | PENDING_VALIDATION | ACCEPTED | REJECTED`

## Immutability

The original `station_id`, `timestamp`, `temperature`, `pressure`, and `humidity` are source data and must not be silently overwritten.

Missing values remain missing until a separate recovery module creates a suggestion.

If an incompatible schema change occurs, increment `schema_version`.
