# SkyGuard AI Implementation Analysis

## 1. Executive Summary

SkyGuard AI is currently a documented MVP architecture with a mostly empty implementation. The documentation under `skyguard-ai-mvp-documentation/` is extensive and internally consistent about the intended product: a local Python + Streamlit/Plotly prototype for AWS anomaly detection using deterministic QC, Isolation Forest, contextual verification, explainability, health scoring, maintenance recommendations, and optional suggested correction/data recovery.

The actual implementation does not yet provide a working MVP. Most top-level source, dashboard, example, and test files are zero-byte placeholders. The only substantive source file found is `src/schemas.py`, which defines Pydantic telemetry models, physical limits, column lists, and a dataframe validator. Even that schema does not match the canonical documentation exactly: documentation centers on `temperature`, `pressure`, and `humidity`, while `src/schemas.py` uses `temperature_c`, `surface_pressure_hpa`, and `relative_humidity_pct` plus additional wind, solar, precipitation, battery, and signal fields.

Current readiness is therefore architectural/planning readiness, not coding readiness for feature integration. The first implementation task should be to normalize the data contract and configuration layer before building simulator, anomaly injection, preprocessing, QC, Isolation Forest, pipeline orchestration, and dashboard.

## 2. Repository Audit

Observed repository structure:

```text
D:\skyguard_ai
|-- README.md                         empty
|-- requirements.txt                   empty
|-- run.py                             empty
|-- dashboard/
|   |-- app.py                         empty
|   `-- __init__.py                    empty
|-- data/
|   |-- raw/
|   |-- processed/
|   `-- simulated/
|-- examples/
|   |-- demo_spike.py                  empty
|   |-- demo_weather_event.py          empty
|   `-- sample_input.csv               empty
|-- models/
|-- notebooks/
|-- reports/
|   |-- evaluation/
|   `-- figures/
|-- skyguard-ai-mvp-documentation/
|   |-- prd.md
|   |-- architecture.md
|   |-- design.md
|   |-- implementation-plan.md
|   |-- data-schema.md
|   |-- qc-rules.md
|   |-- ml-spec.md
|   |-- evaluation.md
|   |-- tech-stack.md
|   |-- api-spec.md
|   |-- README.md
|   |-- DOCUMENTATION_INDEX.md
|   |-- requirements.txt
|   |-- .env.example
|   `-- .gitignore
|-- src/
|   |-- schemas.py                     non-empty
|   |-- anomaly_injector.py            empty
|   |-- config.py                      empty
|   |-- data_simulator.py              empty
|   |-- event_classifier.py            empty
|   |-- explainability.py              empty
|   |-- feature_engineering.py         empty
|   |-- isolation_forest_model.py      empty
|   |-- maintenance.py                 empty
|   |-- pipeline.py                    empty
|   |-- preprocessing.py               empty
|   |-- rule_checks.py                 empty
|   |-- scoring.py                     empty
|   |-- sensor_health.py               empty
|   |-- spatial_consistency.py         empty
|   `-- __init__.py                    empty
`-- tests/
    |-- test_anomaly_detection.py      empty
    |-- test_classification.py         empty
    |-- test_features.py               empty
    |-- test_health.py                 empty
    |-- test_pipeline.py               empty
    |-- test_rules.py                  empty
    |-- test_spatial.py                empty
    `-- __init__.py                    empty
```

Additional observations:

- `.venv/` exists locally and contains installed packages, but it should be ignored for architecture and implementation status.
- No `.git` repository was detected from `D:\skyguard_ai`; `git status --short` failed with `fatal: not a git repository`.
- `pytest -q` using the local venv returned `no tests ran in 0.04s`.
- No model artifacts were found in `models/`.
- No usable sample data was found; `examples/sample_input.csv` is empty.

## 3. Current Implementation Status

Implemented with evidence:

- `src/schemas.py` defines:
  - `AnomalyType`
  - `SensorType`
  - `StationMetadata`
  - `WeatherTelemetryRecord`
  - `PHYSICAL_LIMITS`
  - `TELEMETRY_COLUMNS`
  - `NUMERIC_METEOROLOGICAL_COLUMNS`
  - `DIAGNOSTIC_COLUMNS`
  - `validate_telemetry_dataframe(df)`

Partially implemented:

- Schema validation exists, but it is not aligned with the documented MVP schema and includes broader telemetry fields outside the core MVP.
- Physical range metadata exists, but deterministic QC rules are not implemented as rule result objects.
- A Pydantic model validator contains placeholder consistency checks for dew point and wind gust, but it does not emit errors, warnings, or machine-readable QC results.

Missing:

- Configuration layer.
- Data simulator.
- Historical adapter.
- Anomaly injector.
- Preprocessing.
- QC rule engine.
- Feature engineering.
- Isolation Forest training/inference.
- Temporal verification.
- Spatial verification.
- Event-vs-fault classifier.
- SHAP explainability.
- Severity and confidence scoring.
- Sensor health scoring.
- Maintenance recommendation engine.
- Suggested correction/data recovery.
- Pipeline orchestration.
- Streamlit dashboard.
- Replay/demo workflow.
- Evaluation runner and reports.
- Tests with assertions.
- Working README, run script, and requirements at repository root.

Broken/problematic:

- Top-level `requirements.txt` is empty, so a fresh install from the repository root will not install required dependencies.
- Top-level `README.md` is empty, so the repository lacks runnable instructions.
- All test files are empty, so existing tests provide no validation.
- Existing source module names imply functionality that does not exist yet.
- Schema terminology is inconsistent with the canonical documentation.

## 4. Requirements Traceability Matrix

| Requirement | Documentation Source | Expected Behavior | Existing Implementation | File/Function | Status | Missing Work | Tests Required |
|---|---|---|---|---|---|---|---|
| Core observation ingestion | `prd.md`, `data-schema.md`, `api-spec.md` | Accept `station_id`, `timestamp`, `temperature`, `pressure`, `humidity`; optional coordinates/elevation | Broader telemetry Pydantic model using different field names | `src/schemas.py::WeatherTelemetryRecord` | [PARTIAL] | Decide canonical schema; implement loader | Valid CSV, malformed CSV, missing required fields |
| Input dataframe validation | `data-schema.md`, `qc-rules.md` | Validate required columns, types, nulls, range issues | Checks required telemetry columns and range counts | `validate_telemetry_dataframe` | [PARTIAL] | Align fields and return structured errors | Missing columns, null values, invalid bounds |
| Physical range validation | `qc-rules.md` | Rule result with rule ID, severity, flag, message | Physical limits constants exist; no QC result engine | `PHYSICAL_LIMITS` | [PARTIAL] | Implement range rule module | Boundary, below min, above max, missing |
| Missing/communication detection | `prd.md`, `qc-rules.md` | Detect missing values and timestamp gaps | Null counts only; no gap detection | `validate_telemetry_dataframe` | [PARTIAL] | Add missingness and expected-interval logic | Missing values, gaps, repeated gaps |
| Duplicate timestamp detection | `prd.md` | Identify duplicate station/timestamp observations | Not implemented | none | [MISSING] | Add preprocessing duplicate checks | Duplicate per station/timestamp |
| Temporal ordering | `prd.md`, `api-spec.md` | Deterministic ordering before temporal features | Not implemented | none | [MISSING] | Sort by station/timestamp in preprocessing | Unordered input |
| Step/rate checks | `qc-rules.md` | Compare current vs previous over elapsed time | Thresholds exist in limits; no rule | `PHYSICAL_LIMITS` | [PARTIAL] | Implement stateful rate checks | Normal changes, excessive changes, irregular intervals |
| Persistence/frozen detection | `prd.md`, `qc-rules.md` | Detect repeated identical or near-identical values | Not implemented | none | [MISSING] | Implement rolling persistence rule | Frozen, near-frozen, legitimate short repeats |
| Dew point calculation | `qc-rules.md`, `ml-spec.md` | Magnus-Tetens-derived dew point feature/check | No calculation; only optional `dew_point_c` field | `WeatherTelemetryRecord` | [MISSING] | Implement dew point function | Known T/RH examples, RH edge cases |
| Thermodynamic consistency | `qc-rules.md` | Check dew point <= temperature with tolerance | Placeholder `pass` only | `validate_physical_consistency` | [BROKEN] | Return explicit QC violation | Dew point greater than temperature |
| Cross-variable consistency | `qc-rules.md`, `ml-spec.md` | Use T/P/RH relationships as evidence | Not implemented | none | [MISSING] | Define simple MVP rules/features | Plausible and inconsistent combinations |
| Feature engineering | `ml-spec.md` | Raw, temporal, derived, optional spatial features | Not implemented | empty file | `src/feature_engineering.py` | [MISSING] | Build feature vector contract | Feature columns, no leakage, missing handling |
| Isolation Forest | `prd.md`, `ml-spec.md` | Fit on clean baseline, infer score/is_anomaly/model_version | Not implemented | empty file | `src/isolation_forest_model.py` | [MISSING] | Implement train/predict/persist | Fit, predict, deterministic seed, model unavailable |
| Avoid training leakage | `ml-spec.md` | Do not train on injected anomalies | Not implemented | none | [MISSING] | Use labels/source split in training | Training excludes anomalous rows |
| Scaling policy | `ml-spec.md` | Fit scaler only on baseline if used | Not implemented | none | [MISSING] | Decide whether scaler needed | Scaler fit/persist/inference consistency |
| Temporal verification | `architecture.md`, `prd.md` | Use recent trajectory/persistence as evidence | Not implemented | none | [MISSING] | Add simple non-LSTM temporal evidence | Spike, drift, frozen windows |
| LSTM Autoencoder | `prd.md`, `ml-spec.md` | Advanced optional temporal model | Not implemented | no file | none | [FUTURE] | Do not build for MVP unless later requested | Independent advanced model tests |
| Spatial verification | `prd.md`, `architecture.md` | Compare target station against neighbors | Not implemented | empty file | `src/spatial_consistency.py` | [MISSING] | Implement neighbor median/deviation/consensus | Isolated fault, regional event, missing neighbors |
| Weather event vs sensor fault | `prd.md`, `architecture.md` | Combine evidence into `NORMAL`, `SENSOR_FAULT`, `WEATHER_EVENT`, `UNCERTAIN` | Not implemented | empty file | `src/event_classifier.py` | [MISSING] | Implement explicit evidence fusion | Regional event vs isolated fault |
| Fault taxonomy | `prd.md`, `data-schema.md` | Spike, Frozen/Stuck, Drift/Bias, Communication/Missing | `AnomalyType` contains noncanonical extra labels and lowercase terms | `AnomalyType` | [PARTIAL] | Align enum or map internal labels to canonical output | Taxonomy mapping tests |
| Severity scoring | `prd.md` | Low/Medium/High from evidence | Not implemented | empty file | `src/scoring.py` | [MISSING] | Implement transparent rule-based scoring | Severity cases and boundary logic |
| Confidence scoring | `prd.md` | Evidence strength, not accuracy | Not implemented | empty file | `src/scoring.py` | [MISSING] | Define confidence contract without fabricated metrics | Confidence from evidence combinations |
| SHAP explanation | `prd.md`, `ml-spec.md` | Feature attribution, not causal proof | Not implemented | empty file | `src/explainability.py` | [MISSING] | Add optional SHAP wrapper and fallback | SHAP available/unavailable behavior |
| Plain-English explanation | `design.md` | Operator-readable evidence summary | Not implemented | empty file | `src/explainability.py` | [MISSING] | Generate explanation from evidence payload | Explanation includes no causal overclaim |
| Sensor health | `prd.md`, `design.md` | Rolling health score and status | Not implemented | empty file | `src/sensor_health.py` | [MISSING] | Implement trend-based state update | Repeated faults lower health; recovery stabilizes |
| Maintenance recommendation | `prd.md` | Map sustained degradation/faults to actions | Not implemented | empty file | `src/maintenance.py` | [MISSING] | Implement deterministic recommendation rules | Drift, frozen, communication, high anomaly frequency |
| Suggested correction/data recovery | `prd.md` | Preserve original, store suggestion separately | Not implemented | none | none | [FUTURE] | Keep optional; implement later after core evidence | Original immutable; suggestion separate |
| Pipeline orchestration | `architecture.md`, `api-spec.md` | `process_observation`, `process_batch`, replay flow | Not implemented | empty file | `src/pipeline.py` | [MISSING] | Orchestrate modules with structured result | Normal, anomaly, missing, ML unavailable |
| Dashboard | `design.md`, `prd.md` | Streamlit/Plotly operator console | Not implemented | empty file | `dashboard/app.py` | [MISSING] | Build after pipeline contract is stable | Smoke test dashboard imports and renders |
| Replay workflow | `prd.md`, `api-spec.md` | Row-by-row processing with latency measurement | Not implemented | empty files | `run.py`, `dashboard/app.py` | [MISSING] | Add generator and UI controls | Replay order, pause/reset, latency metadata |
| Evaluation | `evaluation.md` | Clean data + controlled injection + ground truth + metrics | Not implemented | none | none | [MISSING] | Add evaluation runner/report | Precision/recall/F1, latency, classification metrics |
| Root README | `README.md`, docs README | Install/run/test instructions | Empty | `README.md` | [BROKEN] | Populate only after runnable commands exist | Documentation smoke check |
| Dependencies | `tech-stack.md`, docs requirements | Explicit packages | Root requirements empty; docs requirements non-empty | `requirements.txt` | [BROKEN] | Sync root requirements with actual imports | Fresh environment install |

## 5. Architecture Validation

The intended canonical architecture is valid for the project and should be preserved:

```text
VALIDATE
  -> DETECT
  -> VERIFY
  -> EXPLAIN
  -> DIAGNOSE
  -> RECOVER
```

The intended intelligence pipeline is:

```text
AWS Data
-> Data Validation / Preprocessing
-> Physics & Rule-Based QC
-> Feature Engineering
-> Isolation Forest
-> Temporal Verification
-> Spatial Verification
-> Weather Event vs Sensor Fault Decision
-> SHAP Explanation
-> Root Cause Classification
-> Severity + Confidence
-> Sensor Health
-> Maintenance Recommendation
-> Suggested Correction / Data Recovery
-> Dashboard
```

No existing code contradicts this architecture because almost no operational code exists. The primary architectural decision needed before implementation is the canonical field naming and result schema.

## 6. Documentation vs Code Discrepancies

- Documentation requires core variables named `temperature`, `pressure`, and `humidity`; code uses `temperature_c`, `surface_pressure_hpa`, and `relative_humidity_pct`.
- Documentation says optional station metadata may include latitude, longitude, and elevation; code makes latitude, longitude, and elevation required for `WeatherTelemetryRecord`.
- Documentation standardizes root causes as `Spike`, `Frozen/Stuck`, `Drift/Bias`, and `Communication/Missing`; code defines additional anomaly types such as `out_of_bounds`, `physical_inconsistency`, `sensor_degradation`, and `rapid_fluctuation`.
- Documentation says deterministic QC rules should return machine-readable result objects; code only returns dataframe validation summaries and Pydantic field validation.
- Documentation describes a working Streamlit dashboard; `dashboard/app.py` is empty.
- Documentation describes tests; test files exist but contain no assertions.
- Documentation README gives commands such as `streamlit run dashboard/app.py`, `pytest`, and `python run.py`; the root files needed for those commands are empty or nonfunctional.
- Documentation lists dependencies in `skyguard-ai-mvp-documentation/requirements.txt`; root `requirements.txt` is empty.
- Documentation includes SHAP and TensorFlow/Keras as optional/advanced dependencies; no implementation exists for either.

## 7. Missing Components

Required for MVP:

- Canonical schemas and enums.
- Configuration thresholds.
- Data loading and simulator.
- Controlled anomaly injection with ground truth.
- Preprocessing and validation.
- Deterministic QC rule engine.
- Feature engineering.
- Isolation Forest model wrapper.
- Basic temporal evidence from recent windows.
- Basic event/fault classification.
- Severity and confidence scoring.
- Pipeline orchestration.
- Streamlit/Plotly dashboard.
- Replay flow.
- Evaluation runner.
- Tests.
- Root README and requirements.

Important but can follow first MVP skeleton:

- Spatial consistency.
- SHAP explanations.
- Sensor health.
- Maintenance recommendations.

Advanced/future:

- LSTM Autoencoder.
- Sophisticated recovery/reconstruction.
- MQTT/Kafka/WIS2.0.
- Cloud deployment.
- Auth.
- Production DB.
- ESP32/edge deployment.

## 8. Broken/Problematic Components

- Empty test suite creates a false impression of coverage.
- Empty source modules create a false impression of implementation breadth.
- `validate_physical_consistency` checks do nothing when violations occur.
- Schema is broader than MVP, increasing implementation risk before the core T/P/RH path works.
- Required latitude/longitude/elevation in code conflicts with docs where those fields are optional.
- No root dependency file means the project is not reproducible from the repository root.
- No evaluation artifacts exist, so no performance claims are currently supportable.

## 9. MVP Scope

P0 required for functioning MVP:

- Data schema for `station_id`, `timestamp`, `temperature`, `pressure`, `humidity`, optional metadata.
- Local CSV loader and synthetic simulator.
- Anomaly injection for Spike, Frozen/Stuck, Drift/Bias, Communication/Missing, isolated station fault, regional event.
- Preprocessing for missing values, duplicates, ordering, timestamp gaps.
- Deterministic QC for range, step/rate, persistence, dew point/thermodynamic checks.
- Feature engineering for raw, deltas, rolling summaries, persistence counts, dew point.
- Isolation Forest training/inference using clean baseline data.
- Basic classification into canonical taxonomy.
- Pipeline result object.
- Streamlit/Plotly dashboard using pipeline outputs.
- Replay/demo workflow.
- Evaluation with injected ground truth.
- Unit and integration tests.

## 10. Advanced Scope

P1 important intelligence/features:

- Temporal verification beyond simple deltas.
- Spatial consistency with neighbor median/deviation/regional consensus.
- Weather event vs sensor fault classification.
- SHAP feature attribution.
- Sensor health score.
- Maintenance recommendation.
- Suggested Correction / Data Recovery using simple temporal/spatial estimates, only when clearly separated from original observations.

P2 advanced/optional:

- LSTM Autoencoder.
- Advanced seasonal modeling.
- More sophisticated recovery validation.
- Confidence calibration.
- Model drift/retraining workflow.

## 11. Future Scope

P3 future/production:

- MQTT/Kafka live ingestion.
- WIS2.0 integration.
- Production database.
- Cloud deployment.
- Authentication and roles.
- ESP32/edge implementation.
- Production audit logging and model governance.
- Formal predictive maintenance model with failure-date prediction.

## 12. Data Flow

Normal observation:

```text
AWS-01, 2026-01-01T12:00:00, temperature=31.4, pressure=1008.2, humidity=61.0
-> schema validation passes
-> preprocessing preserves original values and orders by timestamp
-> QC rules pass
-> features generated
-> Isolation Forest returns normal evidence
-> temporal/spatial context consistent or unavailable
-> result status NORMAL
-> health maintained
-> dashboard updates metric cards and trends
```

Temperature spike:

```text
AWS-01 jumps from 31.4 C to 55.0 C while neighbors are near 31 C
-> range may pass or fail depending configured local limit
-> step/rate rule fails
-> Isolation Forest likely anomalous
-> temporal evidence shows abrupt isolated jump
-> spatial evidence shows target deviates from neighbors
-> event_type SENSOR_FAULT
-> root_cause Spike
-> severity/confidence derived from evidence strength
```

Frozen/stuck temperature sensor:

```text
AWS-01 reports identical or near-identical temperature across a configured window
-> persistence rule fails
-> temporal evidence shows absent variation
-> root_cause Frozen/Stuck
-> repeated occurrences lower sensor health
-> maintenance recommends inspection of sensing element or firmware path
```

Temperature drift/bias:

```text
AWS-01 gradually diverges from its baseline and/or neighbors
-> individual observations may pass range and step checks
-> rolling slope/deviation features grow
-> Isolation Forest and temporal/spatial evidence may flag pattern
-> root_cause Drift/Bias
-> maintenance recommends inspection/recalibration
```

Missing/communication failure:

```text
Expected timestamp is absent or core values are null
-> missingness/gap rule fails
-> ML is skipped or receives explicit missing-evidence state
-> root_cause Communication/Missing
-> health decreases based on repeated gaps
-> recommendation targets power/network/telemetry path
```

Genuine regional weather event:

```text
AWS-01 = 42.0 C, AWS-02 = 41.5 C, AWS-03 = 42.3 C
-> value may be unusual versus baseline
-> neighbors show regional consensus
-> event_type WEATHER_EVENT or UNCERTAIN, not automatic sensor fault
-> dashboard shows contextual alert
```

Isolated sensor fault:

```text
AWS-01 = 55.0 C, neighboring stations around 31 C
-> target strongly deviates from spatial context
-> event_type SENSOR_FAULT
-> likely root cause Spike if abrupt, Drift/Bias if gradual, Frozen/Stuck if persistent, Communication/Missing if absent
```

## 13. Module Architecture

Recommended module responsibilities:

| Module | Responsibility |
|---|---|
| `src/config.py` | Thresholds, feature flags, model parameters, paths |
| `src/schemas.py` | Canonical input/output contracts and enums |
| `src/data_simulator.py` | Synthetic clean AWS observations |
| `src/historical_adapter.py` | CSV/Parquet historical loading; create only when needed |
| `src/anomaly_injector.py` | Controlled faults and ground truth labels |
| `src/preprocessing.py` | Ordering, type conversion, duplicate/gap/missing handling |
| `src/rule_checks.py` | Deterministic QC rule results |
| `src/feature_engineering.py` | Raw, derived, temporal, and optional spatial features |
| `src/isolation_forest_model.py` | Fit, predict, save/load Isolation Forest |
| `src/spatial_consistency.py` | Neighbor matching, deviation, consensus |
| `src/event_classifier.py` | Event-vs-fault and root-cause classification |
| `src/explainability.py` | SHAP wrapper and plain-language fallback |
| `src/scoring.py` | Severity and confidence |
| `src/sensor_health.py` | Rolling health state |
| `src/maintenance.py` | Recommendations |
| `src/pipeline.py` | Process observation, batch, replay |
| `dashboard/app.py` | UI only; no duplicated ML/business logic |

## 14. Interface/Data Contracts

Canonical raw observation:

```python
{
    "station_id": str,
    "timestamp": datetime | str,
    "temperature": float | None,
    "pressure": float | None,
    "humidity": float | None,
    "latitude": float | None,
    "longitude": float | None,
    "elevation": float | None,
}
```

Canonical processed result:

```python
{
    "station_id": str,
    "timestamp": str,
    "observation": {
        "temperature": float | None,
        "pressure": float | None,
        "humidity": float | None,
    },
    "quality": {
        "is_valid": bool,
        "rules": list[dict],
    },
    "features": dict,
    "anomaly": {
        "is_anomaly": bool,
        "score": float | None,
        "model_version": str | None,
        "available": bool,
    },
    "context": {
        "event_type": "NORMAL" | "SENSOR_FAULT" | "WEATHER_EVENT" | "UNCERTAIN",
        "temporal_evidence": dict,
        "spatial_evidence": dict,
    },
    "diagnosis": {
        "root_cause": "NONE" | "SPIKE" | "FROZEN_STUCK" | "DRIFT_BIAS" | "COMMUNICATION_MISSING" | "UNKNOWN",
        "severity": "LOW" | "MEDIUM" | "HIGH" | "UNKNOWN",
        "confidence": float | None,
    },
    "explanation": {
        "feature_contributions": dict,
        "plain_language": str,
        "available": bool,
    },
    "health": {
        "score": float | None,
        "status": "HEALTHY" | "WARNING" | "DEGRADING" | "CRITICAL" | "UNKNOWN",
        "trend": str | None,
    },
    "maintenance": {
        "recommendation": str | None,
    },
    "recovery": {
        "original_values": dict,
        "suggested_values": dict,
        "status": "NOT_AVAILABLE" | "NOT_REQUIRED" | "SUGGESTED" | "PENDING_VALIDATION" | "ACCEPTED" | "REJECTED",
    },
    "errors": list[dict],
    "latency_ms": dict,
}
```

Proposed interfaces:

| Interface | Inputs | Outputs | Errors/Invariants |
|---|---|---|---|
| `validate_observation(observation)` | Raw mapping or model | Validated observation plus schema errors | Must preserve source values |
| `preprocess_batch(df, config)` | DataFrame | Ordered dataframe plus preprocessing report | No silent row dropping |
| `run_qc(current, history, config)` | Observation, recent station history | List of rule result dicts | Multiple violations retained |
| `engineer_features(df_or_observation, history, context)` | Observation/history | Feature dict/DataFrame | Fit/infer columns consistent |
| `fit_detector(features, config)` | Clean baseline features | Trained model artifact | Must exclude injected anomalies |
| `detect_anomaly(model, features)` | Model and feature vector | Score, flag, model_version | Explicit unavailable state if model missing |
| `verify_temporal(current, history)` | Current observation and station history | Temporal evidence dict | Requires ordered timestamps |
| `verify_spatial(target, neighbors)` | Target and neighbor observations | Spatial evidence dict | No invented neighbors |
| `classify_event_or_fault(evidence)` | QC, ML, temporal, spatial evidence | Event type and root cause | Must allow UNCERTAIN |
| `explain_anomaly(model, features, evidence)` | Model/features/evidence | Feature attribution and plain language | SHAP is attribution, not causal proof |
| `calculate_severity(evidence)` | Combined evidence | LOW/MEDIUM/HIGH/UNKNOWN | Transparent rules |
| `calculate_confidence(evidence)` | Combined evidence | Numeric confidence or None | Not accuracy/precision/recall |
| `update_sensor_health(station_id, result, previous_state)` | Latest result and state | New health state | Longitudinal, not failure date |
| `generate_maintenance_recommendation(result, health)` | Diagnosis and health | Recommendation string | No predictive failure-date claim |
| `suggest_recovery(observation, context)` | Original observation and evidence | Suggested values separate from original | Optional; never overwrite |
| `process_observation(observation, context, state, config)` | Raw observation and context | Processed result | Central orchestration |
| `process_batch(df, config)` | DataFrame | List/DataFrame of processed results | Deterministic order |
| `replay(df, delay_seconds, config)` | DataFrame and delay | Iterator of processed results | Measures latency |

## 15. Implementation Phases

### PHASE 0 - Repository/setup

- Objective: Make the project installable, importable, and testable.
- Files to create/modify: `requirements.txt`, `README.md`, `src/config.py`, `src/schemas.py`, test scaffolding.
- Functions/classes: settings dataclass/Pydantic settings, canonical enums, result models.
- Dependencies: Python 3.10+, pandas, numpy, pydantic, pytest.
- Inputs: documentation requirements.
- Outputs: stable config and schema contract.
- Acceptance criteria: dependencies install; `pytest` runs and collects tests; root README has accurate commands.
- Unit tests: schema validation and enum values.
- Integration tests: package import smoke test.
- Previous dependencies: none.
- Complexity: Medium.
- Risks: schema churn if not decided early.

### PHASE 1 - Data layer

- Objective: Generate/load clean and labeled AWS data.
- Files: `src/data_simulator.py`, `src/anomaly_injector.py`, optional `src/historical_adapter.py`, `examples/sample_input.csv`.
- Functions/classes: simulator, CSV loader, anomaly injection functions, ground truth schema.
- Dependencies: pandas, numpy.
- Inputs: config, seed, station metadata.
- Outputs: clean dataframe and injected dataframe with labels.
- Acceptance criteria: deterministic synthetic datasets for normal, spike, frozen, drift, communication gap, regional event, isolated fault.
- Unit tests: generated schema, deterministic seed, label correctness.
- Integration tests: load generated data into preprocessing.
- Previous dependencies: Phase 0.
- Complexity: Medium.
- Risks: unrealistic data causing misleading evaluation.

### PHASE 2 - Preprocessing + QC

- Objective: Validate and flag data quality/physics issues.
- Files: `src/preprocessing.py`, `src/rule_checks.py`, `src/config.py`.
- Functions/classes: duplicate check, gap check, range check, step/rate check, persistence check, dew point calculation.
- Dependencies: pandas, numpy.
- Inputs: raw dataframe/observation history.
- Outputs: preprocessing report and QC result list.
- Acceptance criteria: each QC rule returns machine-readable evidence; originals preserved.
- Unit tests: normal, boundary, invalid, missing, duplicate, gap, persistence, dew point.
- Integration tests: QC on injected scenarios.
- Previous dependencies: Phases 0-1.
- Complexity: Medium.
- Risks: hardcoded thresholds and silent mutation.

### PHASE 3 - Feature engineering

- Objective: Build reproducible feature vectors for ML and decision logic.
- Files: `src/feature_engineering.py`.
- Functions/classes: raw feature builder, delta features, rolling stats, persistence counts, dew point.
- Dependencies: pandas, numpy.
- Inputs: preprocessed observations and history.
- Outputs: model-ready feature dataframe and feature metadata.
- Acceptance criteria: stable feature columns; no target leakage; missing handling explicit.
- Unit tests: feature column presence, deltas, rolling windows, missing data.
- Integration tests: features generated from simulator output.
- Previous dependencies: Phases 0-2.
- Complexity: Medium.
- Risks: leakage from labels or future observations.

### PHASE 4 - Isolation Forest

- Objective: Implement the primary MVP multivariate detector.
- Files: `src/isolation_forest_model.py`, `models/`.
- Functions/classes: `fit`, `predict`, `save`, `load`.
- Dependencies: scikit-learn, joblib.
- Inputs: clean baseline features.
- Outputs: anomaly score, flag, model version.
- Acceptance criteria: train only on clean baseline; deterministic random seed; explicit unavailable state.
- Unit tests: train/predict/persist.
- Integration tests: injected anomalies produce pipeline-consumable model evidence.
- Previous dependencies: Phases 0-3.
- Complexity: Medium.
- Risks: contamination and score misinterpretation.

### PHASE 5 - Temporal/spatial verification

- Objective: Add context that separates isolated sensor faults from regional events.
- Files: `src/spatial_consistency.py`, temporal helpers in `src/feature_engineering.py` or a small dedicated module if justified.
- Functions/classes: neighbor selection, median/MAD deviation, regional consensus, temporal trajectory evidence.
- Dependencies: pandas, numpy.
- Inputs: target observation, station history, neighbor observations.
- Outputs: temporal and spatial evidence dicts.
- Acceptance criteria: isolated fault and regional event demos produce different evidence.
- Unit tests: missing neighbors, isolated station, regional consensus.
- Integration tests: classifier consumes context.
- Previous dependencies: Phases 0-4.
- Complexity: Medium.
- Risks: spatial logic without real coordinates or synchronized timestamps.

### PHASE 6 - Classification + explainability

- Objective: Convert evidence into event type, root cause, severity, confidence, and explanations.
- Files: `src/event_classifier.py`, `src/scoring.py`, `src/explainability.py`.
- Functions/classes: event/fault classifier, taxonomy mapper, severity/confidence calculators, SHAP adapter, plain-language explanation builder.
- Dependencies: optional SHAP.
- Inputs: QC, ML, temporal, spatial evidence.
- Outputs: diagnosis and explanation payloads.
- Acceptance criteria: canonical taxonomy only; confidence not presented as model accuracy; SHAP unavailable state supported.
- Unit tests: spike, frozen, drift, missing, uncertain, weather event.
- Integration tests: end-to-end evidence fusion.
- Previous dependencies: Phases 0-5.
- Complexity: Medium to High.
- Risks: overconfident decisions and SHAP causal overclaiming.

### PHASE 7 - Sensor health + recommendations

- Objective: Track station health and generate maintenance advice.
- Files: `src/sensor_health.py`, `src/maintenance.py`.
- Functions/classes: health state update, health status categorization, recommendation rules.
- Dependencies: none beyond pandas/numpy if batch summaries are used.
- Inputs: processed results over time.
- Outputs: health score/status/trend and recommendation.
- Acceptance criteria: repeated anomalies degrade health; recommendations map to fault patterns.
- Unit tests: repeated faults, recovery periods, communication gaps.
- Integration tests: replay updates health over time.
- Previous dependencies: Phases 0-6.
- Complexity: Medium.
- Risks: pretending to predict future failure dates.

### PHASE 8 - Dashboard + replay

- Objective: Build an operator-first Streamlit dashboard consuming structured pipeline results.
- Files: `dashboard/app.py`, `run.py`, possibly `dashboard/components/*.py`.
- Functions/classes: replay iterator, dashboard renderer, metric cards, charts, anomaly table, evidence panels.
- Dependencies: streamlit, plotly.
- Inputs: generated or CSV data and pipeline results.
- Outputs: interactive dashboard and demo replay.
- Acceptance criteria: shows station metrics, trends, anomaly markers, table, explanation, spatial evidence, health, recommendations, recovery unavailable state if not implemented.
- Unit tests: mostly smoke/import and data transformation tests.
- Integration tests: dashboard can run/import against sample scenario.
- Previous dependencies: Phases 0-7.
- Complexity: High.
- Risks: duplicating ML logic inside UI or showing fabricated metrics.

### PHASE 9 - Evaluation

- Objective: Produce reproducible metrics from controlled anomaly injection.
- Files: evaluation module/script, `reports/evaluation/`.
- Functions/classes: evaluation runner, metrics calculator, latency recorder, report writer.
- Dependencies: scikit-learn metrics, pandas.
- Inputs: clean data, injected ground truth, frozen model/config.
- Outputs: precision, recall, F1, false positives, false negatives, latency, root-cause accuracy, event-vs-fault metrics.
- Acceptance criteria: metrics calculated from actual predictions only; no fabricated numbers.
- Unit tests: metric formula correctness.
- Integration tests: full evaluation run on deterministic dataset.
- Previous dependencies: Phases 0-8.
- Complexity: Medium.
- Risks: tuning against final test set and reporting unstable metrics.

### PHASE 10 - Testing + integration

- Objective: Turn placeholder tests into meaningful coverage.
- Files: all `tests/test_*.py`.
- Functions/classes: fixtures for sample observations, scenarios, config, model.
- Dependencies: pytest.
- Inputs: implemented modules.
- Outputs: passing test suite.
- Acceptance criteria: core pipeline tests pass; empty tests removed/replaced.
- Unit tests: all modules.
- Integration tests: normal, spike, frozen, drift, missing, regional event, isolated fault.
- Previous dependencies: all implementation phases.
- Complexity: Medium.
- Risks: brittle tests tied to exact ML thresholds.

### PHASE 11 - Final MVP packaging

- Objective: Make the MVP runnable and honestly documented.
- Files: `README.md`, `requirements.txt`, `examples/`, `reports/evaluation/`, `run.py`.
- Functions/classes: CLI/demo entry point.
- Dependencies: final resolved stack.
- Inputs: working code and evaluation reports.
- Outputs: reproducible demo package.
- Acceptance criteria: fresh install works; dashboard and tests run; docs match implementation; no unsupported claims.
- Unit tests: not applicable beyond smoke checks.
- Integration tests: fresh environment command sequence.
- Previous dependencies: Phases 0-10.
- Complexity: Low to Medium.
- Risks: documentation drifting from actual behavior.

## 16. Detailed Coding Order

1. Canonical schemas and enums in `src/schemas.py`.
2. Configuration and thresholds in `src/config.py`.
3. Root `requirements.txt`.
4. Basic import and schema tests.
5. CSV loader and synthetic simulator.
6. Controlled anomaly injector with ground truth labels.
7. Preprocessing: ordering, duplicates, missingness, gaps.
8. QC rule result contract and physical range rules.
9. Step/rate, persistence, dew point, thermodynamic checks.
10. Feature engineering for raw, derived, and temporal features.
11. Isolation Forest model wrapper.
12. Pipeline orchestration for `process_observation` and `process_batch`.
13. Basic root-cause classification.
14. Temporal evidence helpers.
15. Spatial consistency.
16. Event-vs-fault classifier.
17. Severity and confidence scoring.
18. Plain-language explanations.
19. Optional SHAP attribution with unavailable fallback.
20. Sensor health.
21. Maintenance recommendations.
22. Replay iterator and latency measurement.
23. Streamlit dashboard consuming pipeline outputs.
24. Evaluation runner and metric reports.
25. Replace all placeholder tests with actual tests.
26. Root README and examples.
27. Final consistency review against docs and MVP claims.

Suggested correction/data recovery should be delayed until the core detection, classification, spatial context, and evaluation are stable.

## 17. Testing Strategy

Testing should be layered:

- Schema tests: valid records, invalid records, optional metadata, canonical enums.
- Data tests: deterministic simulator, scenario labels, anomaly injection windows.
- Preprocessing tests: missing values, duplicates, timestamp gaps, ordering.
- QC tests: range, step/rate, persistence, dew point, thermodynamic consistency.
- Feature tests: feature columns, deltas, rolling windows, missing handling, no future leakage.
- ML tests: clean training, deterministic seed, prediction output shape, persistence.
- Spatial tests: neighbor unavailable, isolated fault, regional event.
- Classification tests: Spike, Frozen/Stuck, Drift/Bias, Communication/Missing, Weather Event, Uncertain.
- Scoring tests: severity/confidence are separate and evidence-derived.
- Explanation tests: SHAP unavailable fallback and no causal wording.
- Health tests: repeated faults degrade health, healthy periods stabilize.
- Pipeline tests: normal, fault, missing, ML unavailable, spatial unavailable.
- Dashboard smoke tests: import/render helper functions without embedding ML logic.
- Evaluation tests: metric formula correctness and ground truth comparison.

## 18. Evaluation Strategy

Evaluation must use:

```text
Clean dataset
+
Controlled anomaly injection
+
Ground truth
+
Model predictions
```

Required calculations:

- Precision = `TP / (TP + FP)`
- Recall = `TP / (TP + FN)`
- F1 = `2 * precision * recall / (precision + recall)`
- False positives and false negatives from prediction-vs-ground-truth labels.
- Detection latency from measured processing timestamps.
- Root-cause classification accuracy from predicted taxonomy vs injected labels.
- Event-vs-fault performance from `WEATHER_EVENT`, `SENSOR_FAULT`, and `UNCERTAIN` outputs.

No metric value should be reported until generated by a reproducible evaluation run with frozen data, config, and model.

## 19. Risks

- Schema mismatch between docs and code can poison every downstream module.
- Empty placeholder files may cause future developers to overestimate implementation progress.
- Hardcoded thresholds could make demos look good but reduce credibility.
- Training Isolation Forest on injected anomalies would create data leakage.
- Feature engineering can accidentally use future observations in rolling windows.
- Spatial logic can be misleading without synchronized timestamps or real station metadata.
- Confidence can be mistaken for model accuracy unless labeled carefully.
- SHAP can be overclaimed as causal proof.
- Suggested recovery can violate data integrity if it overwrites observations.
- Dashboard can drift into business logic if it does not consume structured pipeline results.
- Evaluation metrics can be fabricated accidentally if placeholder/demo values enter the UI.

## 20. Acceptance Criteria

The MVP is acceptable only when:

- A fresh environment installs dependencies from root `requirements.txt`.
- `pytest` collects and runs meaningful tests.
- A documented CSV or simulated dataset can be loaded.
- Controlled anomalies can be injected with ground truth.
- Original observations remain immutable.
- QC returns structured rule evidence.
- Isolation Forest trains on clean baseline data and produces anomaly evidence.
- Basic root-cause classification uses the canonical taxonomy.
- Spatial context can demonstrate isolated fault vs regional weather event.
- Severity and confidence are calculated from evidence and kept separate from evaluation metrics.
- Dashboard displays current metrics, trends, anomalies, evidence, diagnosis, health, and maintenance.
- Replay processes rows in timestamp order and measures latency.
- Evaluation computes metrics from actual predictions.
- Documentation and UI do not claim unimplemented capabilities.

## 21. Definition of Done

Done means:

1. The local app runs from documented commands.
2. The full pipeline processes simulated or CSV AWS observations.
3. Normal, spike, frozen/stuck, drift/bias, communication/missing, regional event, and isolated fault scenarios are demonstrable.
4. Isolation Forest is the primary MVP multivariate detector.
5. Contextual evidence changes event-vs-fault interpretation.
6. Every processed result preserves original values.
7. Suggested Correction / Data Recovery, if present, is clearly separated and validation-oriented.
8. Tests pass and cover core modules.
9. Evaluation metrics are reproducible and not invented.
10. Dashboard, README, and documentation match actual implementation status.

## 22. Recommended Next Step

Do not begin feature implementation until the canonical schema is settled. The first coding task should be Phase 0: normalize `src/schemas.py` and `src/config.py` around the documented MVP contract, then create real tests for that contract. This prevents the whole system from being built on incompatible field names.

## IMPLEMENTATION READINESS

- Ready to code? NO
- Blocking issues:
  - Canonical schema mismatch between documentation and `src/schemas.py`.
  - Root `requirements.txt` is empty.
  - Almost all implementation files are empty placeholders.
  - Test files are empty; `pytest` reports no tests ran.
  - No sample data, trained model, dashboard, pipeline, or evaluation runner exists.
- Non-blocking issues:
  - Existing `src/schemas.py` can be reused as a starting point.
  - Documentation is strong enough to guide implementation.
  - Directory structure broadly matches the intended architecture.
  - Local `.venv` already contains many likely dependencies, but reproducibility must come from `requirements.txt`.
- First implementation task:
  - Establish the canonical schema/config contract and add tests for it.
- Files that should be touched first:
  - `src/schemas.py`
  - `src/config.py`
  - `requirements.txt`
  - `tests/test_schemas.py` or the existing closest schema/config test file
  - `README.md` after runnable commands are real

