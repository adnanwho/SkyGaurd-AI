# SkyGuard AI — API and Internal Interfaces

## MVP principle

A REST API is **not required** for the first local prototype.

Primary path:

```text
Streamlit → Pipeline → Processing Modules
```

## Pipeline

Conceptual:

```python
result = process_observation(observation, context=None, config=None)
```

Input:
```python
{
    "station_id": "AWS-01",
    "timestamp": "...",
    "temperature": 31.4,
    "pressure": 1008.2,
    "humidity": 61.0
}
```

Output:
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

## Batch

```python
results = process_batch(dataframe, config=None)
```

## Replay

```python
for result in replay(dataframe, delay_seconds=...):
    update_dashboard(result)
```

## Spatial

```python
evaluate_spatial_context(target_observation, neighbor_observations)
```

If neighbors are unavailable, return an explicit unavailable state; never invent data.

## Explainability

```python
explain_anomaly(model, features)
```

Return feature contributions and plain-language summary when available.

## Health

```python
update_sensor_health(station_id, observation_result, previous_state)
```

## Recovery

```python
suggest_recovery(observation, context)
```

Original and suggested values must remain separate.

## Error contract

```json
{
  "error": {
    "code": "MISSING_REQUIRED_FIELD",
    "message": "Required field 'temperature' is missing.",
    "recoverable": true
  }
}
```

## Future REST candidates

```text
POST /observations
POST /observations/batch
GET /stations
GET /stations/{station_id}/health
GET /anomalies
GET /anomalies/{anomaly_id}
POST /replay
GET /evaluation
```

These are future candidates, not MVP requirements.
