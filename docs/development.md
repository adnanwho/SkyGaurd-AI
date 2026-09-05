# Development

## Run checks

```powershell
python -m pytest -q
python -m py_compile main.py dashboard/app.py
```

## Add a data source

Add a loader under `src/skyguard/ingestion`, normalize it to the canonical observation columns, and pass the resulting dataframe to `src.skyguard.engine.SkyGuardEngine.process`.

## Canonical engine API

Application code should use the structured engine result:

```python
from src.skyguard.engine import SkyGuardEngine

engine = SkyGuardEngine()
result = engine.process(dataframe)
result.summary
result.observations
result.anomalies
result.sensor_health
result.diagnostics
```

`run_pipeline` remains an internal dataframe compatibility function for existing evaluation and replay callers. New adapters and application integrations should use `SkyGuardEngine.process`.

## Add a model

Add model-specific code under `src/skyguard/detection`. Keep feature preparation and model persistence separate from the dashboard. Add focused tests under `tests/unit` and pipeline coverage under `tests/integration`.

## Add dashboard behavior

Keep Streamlit presentation in `dashboard/app.py` or reusable modules under `dashboard/components`. Consume structured pipeline output rather than reimplementing QC or ML logic in the UI.

## Generated files

Use `models/trained`, `models/metadata`, `outputs/exports`, and `outputs/evaluation` for generated artifacts. Do not place generated data in `src` or alongside source modules.
