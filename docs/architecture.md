# Architecture

SkyGuard preserves a layered local MVP pipeline:

```text
Data ingestion
  -> preprocessing and deterministic QC
  -> feature engineering
  -> ensemble detection
  -> temporal/spatial context
  -> diagnosis
  -> explainability
  -> health and operations
  -> structured output and dashboard
```

The canonical implementation is under `src/skyguard`. The dashboard imports pipeline APIs but contains no detection or QC logic. Input adapters normalize observations into the canonical fields `station_id`, `timestamp`, `temperature`, `pressure`, and `humidity`, allowing future live adapters to feed the same pipeline.

## Package map

- `ingestion`: CSV loading, normalization, and schemas
- `preprocessing`: deterministic quality control
- `features`: derived and temporal features
- `detection`: ensemble and persisted baseline models
- `context`: temporal and spatial evidence
- `diagnosis`: event/fault evidence fusion
- `explainability`: SHAP and safe fallbacks
- `health`: sensor health and operational recommendations
- `evaluation`: scenarios, metrics, and reproducible runner
- `replay`: row-by-row batch replay
