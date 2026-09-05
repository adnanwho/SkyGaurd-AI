# SkyGuard AI

SkyGuard AI is a hybrid, explainable quality-control and sensor-health prototype for Automatic Weather Stations (AWS), aligned with SIH26073.

## Core flow

```text
AWS Temperature + Pressure + Humidity
        ↓
Data + Physics QC
        ↓
Isolation Forest
        ↓
Temporal + Spatial Validation
        ↓
Weather Event vs Sensor Fault
        ↓
Explainability
        ↓
Root Cause + Severity + Confidence
        ↓
Sensor Health
        ↓
Suggested Correction / Data Recovery
        ↓
Dashboard
```

## Core fault taxonomy
- Spike
- Frozen/Stuck
- Drift/Bias
- Communication/Missing

## Quick start

```bash
pip install -r requirements.txt
streamlit run dashboard/app.py
pytest
python run.py
```

## Development rules
1. Preserve original observations.
2. Never silently replace source values.
3. Do not fabricate performance metrics.
4. Do not claim advanced modules until implemented and validated.
5. Keep code, documentation, dashboard and presentation consistent.
6. Use “Suggested Correction / Data Recovery” rather than “Self-Healing”.

## MVP

```text
Simulator → Anomaly Injector → Preprocessing → Physics QC
→ Isolation Forest → Basic Classification → Dashboard
```

Spatial validation, SHAP, severity/confidence, sensor health and maintenance form the intelligence layer. LSTM Autoencoder and model-based recovery are advanced/optional. Live MQTT/Kafka/WIS2.0, cloud, authentication and edge deployment are future scope.
