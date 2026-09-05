# SkyGuard AI — Technical Stack

| Technology | Role |
|---|---|
| Python 3.10+ | Application and pipeline |
| NumPy | Numerical operations |
| Pandas | Data/time-series processing |
| Scikit-learn | ML/preprocessing |
| Isolation Forest | Primary anomaly detector |
| Joblib | Model persistence |
| Streamlit | Dashboard |
| Plotly | Interactive visualization |
| Pytest | Testing |
| SHAP | Explainability |
| TensorFlow/Keras | Optional LSTM Autoencoder |

## Storage

Prototype:
`CSV`, `Parquet`

Model artifacts:
`Joblib`

Production database is future scope.

## Architecture style

```text
Modular Python
+
Central pipeline orchestrator
+
Streamlit presentation layer
```

The dashboard consumes structured pipeline results rather than duplicating model logic.

## Dependency policy

Dependencies must be explicit and tested together. The offline demo should not require cloud services.

## Future infrastructure

MQTT, Kafka, WIS2.0, cloud, production databases, authentication and ESP32 toolchains are not MVP requirements.
