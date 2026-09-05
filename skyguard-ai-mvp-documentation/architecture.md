# SkyGuard AI --- System Architecture

**Project:** SkyGuard AI\
**SIH Problem Statement:** SIH26073 --- AI/ML-Based Intelligent Anomaly
Detection for Automatic Weather Stations (AWS)\
**Architecture Version:** 1.0\
**Status:** Development Baseline

------------------------------------------------------------------------

## 1. Architecture Objective

SkyGuard AI is designed as a **hybrid observation-intelligence
pipeline** for detecting and diagnosing anomalies in Automatic Weather
Station observations.

The architecture combines:

1.  Deterministic physical/data-quality validation
2.  Multivariate machine learning
3.  Temporal behavior analysis
4.  Spatial neighboring-station evidence
5.  Explainable AI
6.  Root-cause and severity classification
7.  Sensor-health monitoring
8.  Suggested correction/data recovery
9.  Operator-facing visualization

The central architectural principle is:

> **An unusual observation is not automatically a faulty observation.**

SkyGuard therefore uses multiple layers of evidence to distinguish a
genuine weather event from a local sensor/data anomaly.

------------------------------------------------------------------------

# 2. Canonical Architecture

``` text
┌─────────────────────────────────────────────────────────────────────┐
│                    AWS / SIMULATED DATA STREAM                      │
│                                                                     │
│       Station ID | Timestamp | Temperature | Pressure | Humidity   │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                 STAGE 1 — INGESTION & PRE-FILTER                   │
│                                                                     │
│  • Schema validation                                                │
│  • Timestamp/data-quality checks                                    │
│  • WMO-aligned physical range checks                                │
│  • Step/rate checks                                                  │
│  • Persistence/frozen-value checks                                  │
│  • Thermodynamic consistency                                        │
│  • Magnus-derived dew-point consistency                             │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                    ┌────────────┴────────────┐
                    │                         │
          Physically impossible       Physically plausible
                    │                         │
                    ▼                         ▼
        ┌──────────────────────┐   ┌──────────────────────────────┐
        │ FAST-PATH ALERT      │   │ STAGE 2 — ML / TEMPORAL      │
        │                      │   │                              │
        │ Rule-based anomaly   │   │ • Feature engineering        │
        │ flag; no deep model  │   │ • Isolation Forest           │
        │ required             │   │ • LSTM Autoencoder*          │
        └──────────┬───────────┘   └──────────────┬───────────────┘
                   │                              │
                   └──────────────┬───────────────┘
                                  ▼
┌─────────────────────────────────────────────────────────────────────┐
│             STAGE 3 — TEMPORAL / SPATIAL VERIFICATION              │
│                                                                     │
│  Temporal evidence:                                                 │
│  • Recent trajectory                                                │
│  • Persistence                                                      │
│  • Historical/seasonal behavior                                     │
│                                                                     │
│  Spatial evidence:                                                  │
│  • Neighboring AWS observations                                     │
│  • Local deviation                                                  │
│  • Regional consensus                                               │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│          STAGE 4 — EVENT DECISION / ROOT-CAUSE / SEVERITY           │
│                                                                     │
│  Determine whether evidence is more consistent with:               │
│                                                                     │
│      Genuine Weather Event                                          │
│              OR                                                     │
│      Sensor / Data Fault                                             │
│              OR                                                     │
│      Uncertain / Insufficient Evidence                               │
│                                                                     │
│  Root Cause:                                                         │
│  • Spike                                                            │
│  • Frozen/Stuck                                                     │
│  • Drift/Bias                                                       │
│  • Communication/Missing                                            │
│                                                                     │
│  Output: Severity + Confidence                                      │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                  EXPLAINABILITY LAYER                               │
│                                                                     │
│  • SHAP feature attribution                                         │
│  • Parameter contribution                                           │
│  • Plain-English reasoning                                          │
│  • Evidence summary                                                 │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   SENSOR HEALTH LAYER                               │
│                                                                     │
│  • Rolling health score                                             │
│  • Fault frequency                                                  │
│  • Persistent degradation                                           │
│  • Trend analysis                                                   │
│  • Maintenance recommendation                                       │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│             SUGGESTED CORRECTION / DATA RECOVERY                   │
│                                                                     │
│  • Optional recovery/reconstruction                                 │
│  • Original value preserved                                         │
│  • Suggested value stored separately                                 │
│  • Validation required before replacement                            │
└────────────────────────────────┬────────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      STREAMLIT DASHBOARD                            │
│                                                                     │
│  • Station status                                                   │
│  • Live/replay charts                                               │
│  • Anomaly alerts                                                   │
│  • Root cause                                                       │
│  • Severity / confidence                                            │
│  • SHAP explanation                                                 │
│  • Neighbor comparison                                              │
│  • Sensor health                                                    │
│  • Maintenance recommendation                                       │
│  • Suggested recovery                                               │
└─────────────────────────────────────────────────────────────────────┘

* LSTM Autoencoder = advanced/optional module unless implemented and validated.
```

------------------------------------------------------------------------

# 3. Architectural Processing Sequence

The system follows:

> **Validate → Detect → Verify → Explain → Diagnose → Recover**

### Validate

Determine whether the observation is valid and physically plausible.

### Detect

Use multivariate anomaly detection to identify observations that do not
resemble the learned normal baseline.

### Verify

Use temporal and spatial evidence to determine whether the anomaly is
isolated, persistent, contextual or regional.

### Explain

Expose the major feature contributions behind the ML decision.

### Diagnose

Assign likely event/fault type, severity, confidence and sensor-health
implications.

### Recover

Optionally produce a suggested corrected/imputed value while preserving
the original observation.

------------------------------------------------------------------------

# 4. Layer 1 --- Ingestion and Physics Pre-Filter

## 4.1 Input

The minimum observation schema is:

``` text
station_id
timestamp
temperature
pressure
humidity
```

Optional station metadata:

``` text
latitude
longitude
elevation
```

## 4.2 Responsibilities

The ingestion layer is responsible for:

-   Parsing incoming observations
-   Validating schema
-   Ordering observations by timestamp
-   Detecting missing fields
-   Detecting malformed values
-   Detecting duplicate observations
-   Preserving source observations

## 4.3 Physics and QC Rules

The pre-filter applies deterministic checks such as:

``` text
Physical Range
      +
Step / Rate
      +
Persistence
      +
Thermodynamic Consistency
```

The project uses WMO-aligned quality-control concepts.

For temperature and humidity consistency, a Magnus-Tetens-derived
dew-point calculation may be used.

A simplified consistency relationship is:

``` text
Dew Point ≤ Air Temperature
```

The exact implementation thresholds should remain configurable rather
than hard-coded into the architecture document.

------------------------------------------------------------------------

# 5. Fast-Path Processing

One of the important architectural characteristics is a **rules-first
fast path**.

If a value is physically impossible or violates a deterministic quality
rule strongly enough to be immediately actionable, the system can flag
it without waiting for deeper ML processing.

``` text
Observation
    │
    ▼
Physics QC
    │
    ├── Impossible ──► Immediate Rule Alert
    │
    └── Plausible ──► ML / Contextual Analysis
```

Benefits:

-   Low computational overhead
-   Fast response
-   Transparent reasoning
-   Reduced dependence on ML inference
-   Suitable for future resource-constrained deployment

The fast path should not be interpreted as proof that every rule
violation is a sensor fault; the classification layer may still use
contextual evidence.

------------------------------------------------------------------------

# 6. Feature Engineering

The ML pipeline should operate on meteorologically meaningful features
rather than relying only on raw values.

Potential feature groups include:

## 6.1 Raw Features

``` text
temperature
pressure
humidity
```

## 6.2 Temporal Features

``` text
previous value
change from previous observation
rolling mean
rolling standard deviation
short-term slope
persistence count
```

## 6.3 Derived Meteorological Features

Potential examples include:

``` text
dew point
temperature-humidity relationship
pressure change
```

## 6.4 Spatial Features

When neighboring stations are available:

``` text
neighbor median
neighbor MAD / deviation
station-to-neighbor difference
regional consensus
```

Feature availability should depend on the actual dataset and
implementation.

------------------------------------------------------------------------

# 7. Stage 2 --- Multivariate Anomaly Detection

## 7.1 Isolation Forest

Isolation Forest is the **primary multivariate anomaly detector**.

Its purpose is to detect observations that are unusual in the joint
feature space.

For example, each value individually might fall within an acceptable
range:

``` text
Temperature = plausible
Pressure    = plausible
Humidity    = plausible
```

but the combination may be statistically unusual.

The Isolation Forest output becomes one evidence signal in the larger
decision pipeline.

## 7.2 Baseline Training

The model should be trained on an appropriate normal/baseline dataset.

Training data may come from:

-   Historical observations
-   Clean simulated observations
-   Carefully filtered observations

Injected anomalies should not contaminate the baseline training set.

## 7.3 Model Output

Conceptually:

``` text
Feature Vector
      ↓
Isolation Forest
      ↓
Anomaly Score / Flag
```

The score should be retained as model evidence rather than directly
equated with probability.

------------------------------------------------------------------------

# 8. Stage 2 Advanced Temporal Module

## LSTM Autoencoder

The LSTM Autoencoder is an advanced temporal/seasonal anomaly-detection
module.

Conceptually:

``` text
Normal Sequence
      ↓
LSTM Encoder
      ↓
Latent Representation
      ↓
LSTM Decoder
      ↓
Reconstructed Sequence
      ↓
Reconstruction Error
      ↓
Temporal Anomaly Evidence
```

The model is intended to learn normal temporal behavior and identify
sequences that deviate from that learned behavior.

### Important Boundary

The LSTM Autoencoder is **not a mandatory dependency of the core MVP**.

It must not be represented as implemented unless:

-   The model exists in the codebase.
-   It can be trained or loaded.
-   It runs through the pipeline.
-   Its outputs are validated.
-   The dashboard only displays it when active.

------------------------------------------------------------------------

# 9. Stage 3 --- Temporal Verification

Temporal evidence helps determine whether an unusual observation is:

-   A one-time spike
-   A persistent frozen value
-   A gradual drift
-   A normal temporal transition
-   A sequence-level anomaly

Example:

``` text
Normal:
31.0 → 31.1 → 31.2 → 31.3 → 31.4

Spike:
31.0 → 31.1 → 55.0 → 31.3 → 31.4

Drift:
31.0 → 31.4 → 31.8 → 32.2 → 32.6

Frozen:
31.0 → 31.0 → 31.0 → 31.0 → 31.0
```

Temporal evidence is especially important for distinguishing different
fault types.

------------------------------------------------------------------------

# 10. Stage 3 --- Spatial Verification

Spatial validation is one of SkyGuard's key differentiators.

A target station is compared with nearby AWS observations.

## 10.1 Isolated Fault

``` text
Station A = 55°C
Station B = 31°C
Station C = 31.4°C
Station D = 30.8°C
```

Interpretation:

``` text
Strong local deviation
       ↓
Likely station/sensor issue
```

## 10.2 Regional Weather Event

``` text
Station A = 42°C
Station B = 41.7°C
Station C = 42.2°C
Station D = 41.9°C
```

Interpretation:

``` text
Regional consensus
       ↓
Potential genuine weather event
```

This prevents a purely threshold-based system from treating every
extreme value as a faulty sensor.

------------------------------------------------------------------------

# 11. Evidence Fusion

The event decision layer should combine available evidence rather than
depending on one signal.

Conceptually:

``` text
                 ┌── Physics QC
                 │
                 ├── Isolation Forest
                 │
Observation ─────┼── Temporal Evidence
                 │
                 ├── Spatial Evidence
                 │
                 └── Persistence / Missingness
                         │
                         ▼
                 Evidence Fusion
                         │
                         ▼
             Event vs Fault Decision
```

Not every observation will have every evidence source.

For example:

-   A single-station dataset may have no spatial evidence.
-   A missing observation may not produce a conventional ML score.
-   A physics-impossible value may be resolved by the fast path.

The architecture must therefore support partial evidence.

------------------------------------------------------------------------

# 12. Stage 4 --- Event vs Fault Classifier

The decision layer produces one of three broad interpretations:

``` text
GENUINE WEATHER EVENT
LIKELY SENSOR / DATA FAULT
UNCERTAIN
```

The system should avoid false certainty when evidence is insufficient.

## 12.1 Fault Taxonomy

The standardized fault taxonomy is:

``` text
Spike
Frozen/Stuck
Drift/Bias
Communication/Missing
```

## 12.2 Classification Logic

### Spike

Indicators:

-   Sudden change
-   Isolated observation
-   High deviation from local/temporal context

### Frozen/Stuck

Indicators:

-   Repeated identical or near-identical values
-   Lack of expected variation
-   Persistent flatline

### Drift/Bias

Indicators:

-   Gradual persistent deviation
-   Long-term shift from expected behavior
-   Repeated contextual mismatch

### Communication/Missing

Indicators:

-   Missing values
-   Timestamp gaps
-   Telemetry interruption
-   Repeated communication failures

------------------------------------------------------------------------

# 13. Severity Layer

Severity categorizes operational importance.

``` text
LOW
MEDIUM
HIGH
```

Possible evidence:

-   Magnitude of deviation
-   Persistence
-   Number of violated checks
-   ML anomaly strength
-   Spatial isolation
-   Repetition/frequency
-   Potential impact on data quality

Severity is an operational classification and must not be confused with
model accuracy.

------------------------------------------------------------------------

# 14. Confidence Layer

Confidence represents the strength of the available evidence supporting
a classification.

Conceptually:

``` text
Physics Evidence
       +
ML Evidence
       +
Temporal Evidence
       +
Spatial Evidence
       +
Persistence
       ↓
Combined Evidence
       ↓
Confidence
```

Confidence must remain distinguishable from:

``` text
Precision
Recall
F1-score
Probability of failure
```

A confidence score should only be presented when its calculation is
explicitly implemented.

------------------------------------------------------------------------

# 15. Explainability Layer

SHAP is used for feature-level explanation of model decisions.

Conceptually:

``` text
Isolation Forest / Supported Model
                ↓
              SHAP
                ↓
      Feature Contributions
                ↓
      Plain-English Explanation
```

Example:

``` text
Temperature  █████████  High contribution
Humidity     █████      Medium contribution
Pressure     ██         Low contribution
```

The explanation should answer:

> **Which observed features contributed most to this anomaly decision?**

It should not claim:

> **This feature caused the sensor to fail.**

SHAP is an attribution method, not causal proof.

------------------------------------------------------------------------

# 16. Sensor Health Architecture

Sensor health is a longitudinal layer.

A single anomaly does not necessarily mean a degraded sensor.

Conceptually:

``` text
Recent anomaly history
        +
Fault frequency
        +
Persistence
        +
Drift indicators
        +
Recent behavior
        ↓
Rolling Health Calculation
        ↓
Sensor Health Score
        ↓
Health Status
```

Possible operational states:

``` text
Healthy
Warning
Degrading
Critical
```

The initial implementation should remain transparent and trend-based.

A fully predictive failure model requires long-term labeled
maintenance/failure history and is future scope.

------------------------------------------------------------------------

# 17. Maintenance Recommendation Engine

The maintenance layer converts persistent degradation patterns into
technician-readable recommendations.

``` text
Increasing Drift
    → Inspect / recalibrate sensor

Repeated Frozen Values
    → Inspect sensing element / firmware path

Repeated Communication Gaps
    → Inspect power/network/telemetry path

High Anomaly Frequency
    → Inspect sensor health

Low Health + Rising Fault Trend
    → Maintenance recommended
```

The architecture intentionally avoids claiming exact failure-date
prediction.

------------------------------------------------------------------------

# 18. Suggested Correction / Data Recovery

This layer is optional.

When a suitable recovery method is available:

``` text
Corrupted / Missing Observation
            ↓
Recovery Model / Context
            ↓
Suggested Value
```

The data model must preserve both:

``` text
original_value
suggested_value
```

Example:

``` text
Original observation: 55.2°C
Suggested value:      33.7°C
```

The suggested value is a **candidate for validation**, not an automatic
replacement.

The audit trail must remain intact.

------------------------------------------------------------------------

# 19. Dashboard Architecture

The Streamlit dashboard acts as the operator-facing presentation layer.

``` text
                    Pipeline Output
                          │
         ┌────────────────┼─────────────────┐
         │                │                 │
         ▼                ▼                 ▼
    Station View     Anomaly View       Health View
         │                │                 │
         └────────────────┼─────────────────┘
                          │
                          ▼
                   Explanation View
                          │
                          ▼
                   Spatial Comparison
                          │
                          ▼
                  Recovery / Maintenance
```

## Dashboard Panels

### Station Overview

-   Temperature
-   Pressure
-   Humidity
-   Current state
-   Health status

### Time-Series Panel

-   Parameter trends
-   Anomaly markers
-   Historical context

### Anomaly Panel

-   Timestamp
-   Station
-   Anomaly score
-   Root cause
-   Severity
-   Confidence

### Explanation Panel

-   SHAP contribution
-   Plain-English reasoning
-   Supporting evidence

### Spatial Panel

-   Target station
-   Neighbor stations
-   Regional consensus
-   Local deviation

### Health Panel

-   Health score
-   Health trend
-   Maintenance recommendation

### Recovery Panel

When available:

-   Original value
-   Suggested value
-   Recovery evidence
-   Validation state

------------------------------------------------------------------------

# 20. Real-Time Replay Architecture

The prototype uses row-by-row replay to simulate streaming behavior.

``` text
Dataset
   ↓
Read next observation
   ↓
Validate
   ↓
Feature Engineering
   ↓
Physics Rules
   ↓
ML Detection
   ↓
Evidence Fusion
   ↓
Explain
   ↓
Classify
   ↓
Update Health
   ↓
Update Dashboard
   ↓
Wait briefly
   ↓
Read next observation
```

This provides a practical real-time demonstration without requiring
production live telemetry infrastructure.

------------------------------------------------------------------------

# 21. Data Flow

## 21.1 Normal Observation

``` text
Observation
    ↓
QC passes
    ↓
ML normal
    ↓
Context consistent
    ↓
No anomaly
    ↓
Health maintained
    ↓
Dashboard update
```

## 21.2 Sensor Spike

``` text
Observation
    ↓
Possible QC violation
    ↓
Isolation Forest anomaly
    ↓
Temporal spike evidence
    ↓
Neighbor stations normal
    ↓
Likely Sensor Fault
    ↓
Root Cause = Spike
    ↓
Severity / Confidence
    ↓
SHAP explanation
    ↓
Health impact
    ↓
Dashboard alert
```

## 21.3 Regional Weather Event

``` text
Extreme Observation
    ↓
Possible anomaly
    ↓
Isolation Forest evidence
    ↓
Neighbor stations also extreme
    ↓
Regional consensus
    ↓
Potential Genuine Weather Event
    ↓
Avoid isolated-sensor fault diagnosis
    ↓
Dashboard contextual alert
```

## 21.4 Communication Failure

``` text
Missing Observation
    ↓
Timestamp / continuity check
    ↓
Communication/Missing
    ↓
Health degradation
    ↓
Maintenance recommendation
```

------------------------------------------------------------------------

# 22. Module Responsibilities

  Module                        Primary Responsibility
  ----------------------------- ---------------------------------
  `config.py`                   Configuration and thresholds
  `schemas.py`                  Input/output data contracts
  `data_simulator.py`           Synthetic AWS data
  `historical_adapter.py`       Historical observation loading
  `anomaly_injector.py`         Controlled anomaly generation
  `preprocessing.py`            Data cleaning/QC preparation
  `feature_engineering.py`      Derived ML/context features
  `rule_checks.py`              Physics and deterministic QC
  `isolation_forest_model.py`   Primary anomaly model
  `lstm_autoencoder.py`         Advanced temporal model
  `spatial_consistency.py`      Neighbor verification
  `event_classifier.py`         Event/fault interpretation
  `explainability.py`           SHAP and explanation generation
  `scoring.py`                  Severity/confidence scoring
  `sensor_health.py`            Longitudinal health score
  `maintenance.py`              Maintenance recommendations
  `pipeline.py`                 End-to-end orchestration
  `dashboard/app.py`            Streamlit/Plotly UI

------------------------------------------------------------------------

# 23. Central Orchestrator

`src/pipeline.py` is the central orchestration layer.

Conceptually:

``` text
process_observation(observation):

    validate_input()

    preprocess()

    rule_results = run_physics_qc()

    features = create_features()

    ml_result = run_isolation_forest()

    temporal_result = run_temporal_analysis_if_enabled()

    spatial_result = run_spatial_validation_if_available()

    decision = classify_event_or_fault(
        rule_results,
        ml_result,
        temporal_result,
        spatial_result
    )

    explanation = generate_explanation()

    severity = calculate_severity()

    confidence = calculate_confidence()

    health = update_sensor_health()

    maintenance = generate_maintenance_recommendation()

    recovery = generate_suggested_recovery_if_enabled()

    return structured_result
```

The exact function names are implementation decisions, but the
responsibilities should remain aligned with this sequence.

------------------------------------------------------------------------

# 24. Output Contract

The pipeline should return a predictable structured result.

Example:

``` json
{
  "station_id": "AWS-01",
  "timestamp": "2026-01-01T12:00:00",
  "status": "ANOMALY",
  "anomaly_score": 0.0,
  "confidence": 0.0,
  "event_type": "SENSOR_FAULT",
  "root_cause": "Spike",
  "severity": "High",
  "explanation": "Temperature contributed strongly to the anomaly.",
  "health_score": 0.0,
  "maintenance_recommendation": "Inspect / recalibrate sensor",
  "original_values": {
    "temperature": 55.2,
    "pressure": 1008.4,
    "humidity": 41.0
  },
  "suggested_values": {
    "temperature": 33.7
  }
}
```

The numbers are structural placeholders only.

------------------------------------------------------------------------

# 25. Error Handling

The pipeline should distinguish:

``` text
VALID OBSERVATION
INVALID INPUT
MISSING DATA
PHYSICAL ANOMALY
ML ANOMALY
CONTEXTUAL ANOMALY
LIKELY SENSOR FAULT
POTENTIAL WEATHER EVENT
UNCERTAIN
```

Failures must be explicit.

The system should not silently:

-   Drop an observation
-   Replace a value
-   Convert a missing value into a prediction
-   Mark an uncertain event as a confirmed fault

------------------------------------------------------------------------

# 26. Storage and Traceability

The prototype can use:

``` text
CSV
Parquet
Joblib
```

Model outputs and anomaly metadata should be retained for traceability.

A conceptual record structure is:

``` text
source observation
       +
QC results
       +
ML results
       +
spatial/temporal evidence
       +
classification
       +
explanation
       +
health state
       +
suggested recovery
```

Original observations remain immutable from the application's correction
layer.

------------------------------------------------------------------------

# 27. Testing Architecture

Tests should be organized around independent modules.

``` text
tests/
├── test_rules.py
├── test_features.py
├── test_anomaly_detection.py
├── test_spatial.py
├── test_classification.py
├── test_health.py
└── test_pipeline.py
```

## Test Categories

### Rule Tests

-   Valid ranges
-   Invalid ranges
-   Step changes
-   Persistence
-   Thermodynamic consistency

### ML Tests

-   Model loads
-   Baseline training works
-   Anomaly injection produces testable outputs

### Spatial Tests

-   Isolated anomaly
-   Regional event
-   Missing neighbor data

### Classification Tests

-   Spike
-   Frozen/Stuck
-   Drift/Bias
-   Communication/Missing

### Pipeline Tests

-   Healthy observation
-   Fault observation
-   Missing observation
-   Full end-to-end processing

------------------------------------------------------------------------

# 28. Evaluation Architecture

The evaluation system should use controlled ground truth.

``` text
Clean Dataset
     ↓
Anomaly Injection
     ↓
Known Ground Truth
     ↓
SkyGuard Pipeline
     ↓
Predictions
     ↓
Metric Calculation
```

Required evaluation metrics include:

-   Precision
-   Recall
-   F1-score
-   False positives
-   False negatives
-   Detection latency
-   Root-cause classification performance

Optional:

-   Confidence calibration
-   Correction quality

------------------------------------------------------------------------

# 29. Deployment Architecture

## MVP

``` text
Local Machine
    │
    ├── Python
    ├── ML Models
    ├── Local Data
    └── Streamlit Dashboard
```

No production cloud dependency is required.

## Future Edge Architecture

Potential future deployment:

``` text
AWS Sensor
     ↓
Edge Device / Gateway
     ↓
Physics QC
     ↓
Lightweight ML
     ↓
Telemetry
     ↓
Central Monitoring
```

Potential future technologies include:

-   MQTT
-   Kafka
-   WIS2.0
-   ESP32
-   Containerized deployment

These are future capabilities and should not be represented as
implemented unless they actually are.

------------------------------------------------------------------------

# 30. Scalability Architecture

The core processing logic should remain station-independent.

``` text
             ┌── Station A ──┐
             │               │
             ├── Station B ──┤
Data Stream ─┼── Station C ──┼──► Processing Pipeline
             │               │
             └── Station N ──┘
```

Spatial validation can use station metadata and neighboring
observations.

The architecture should therefore support:

``` text
Single Station
      ↓
Small Multi-Station Demo
      ↓
Regional Network
      ↓
Large AWS Network
```

Scaling should not require redesigning the core anomaly reasoning logic.

------------------------------------------------------------------------

# 31. Security Architecture

## Prototype

Priorities:

-   Local execution
-   Original-data preservation
-   Traceable outputs
-   Deterministic experiments
-   No unnecessary external API dependency

## Production Future

Production security should eventually include:

``` text
Authenticated ingestion
        ↓
Encrypted transport
        ↓
Access control
        ↓
Audit logging
        ↓
Secure storage
        ↓
Model/version management
        ↓
Backup / recovery
```

Production security controls are future scope unless implemented and
tested.

------------------------------------------------------------------------

# 32. Architecture Boundaries

The following are explicitly **outside the core architecture** unless
deliberately implemented:

-   3 specialized LLM agents
-   18B-parameter architecture
-   70B+ model comparison
-   Agentic architecture
-   Anomaly Knowledge Base as a required reasoning layer
-   Autonomous silent correction
-   Production predictive-maintenance model
-   Live MQTT/Kafka/WIS2.0 infrastructure
-   Cloud-only operation
-   ESP32 firmware deployment

These should not appear in diagrams as existing components unless the
project architecture is intentionally changed.

------------------------------------------------------------------------

# 33. Core vs Advanced vs Future

  Component                       Status
  ------------------------------- ------------------------------
  Data ingestion                  Core
  Preprocessing                   Core
  Physics QC                      Core
  Isolation Forest                Core
  Basic anomaly classification    Core
  Dashboard                       Core
  Evaluation framework            Core
  Spatial validation              Important intelligence layer
  SHAP                            Important intelligence layer
  Severity/confidence             Important intelligence layer
  Sensor health                   Important intelligence layer
  Maintenance recommendations     Important intelligence layer
  LSTM Autoencoder                Advanced/Optional
  Suggested correction            Advanced/Optional
  MQTT/Kafka                      Future
  WIS2.0                          Future
  Cloud deployment                Future
  Authentication                  Future
  ESP32/edge                      Future
  Predictive failure-date model   Future

The implementation status must always override documentation
assumptions.

------------------------------------------------------------------------

# 34. Architecture Decision Principles

### AD-01 --- Rules First

Use deterministic QC before expensive model processing where practical.

### AD-02 --- Isolation Forest as Primary ML Detector

Use Isolation Forest as the primary multivariate detector.

### AD-03 --- Context Matters

Use temporal and spatial evidence before making a strong fault
interpretation.

### AD-04 --- Explain the Decision

Provide feature-level attribution and operator-readable reasoning.

### AD-05 --- Preserve Source Truth

Never silently overwrite the original observation.

### AD-06 --- Graceful Partial Evidence

The pipeline must operate when temporal, spatial or advanced-model
evidence is unavailable.

### AD-07 --- No Unsupported Claims

Architecture diagrams, documentation, dashboard labels and PPT claims
must reflect the actual implementation.

------------------------------------------------------------------------

# 35. Architecture Success Criteria

The architecture is successful when it supports the following complete
flow:

``` text
Raw AWS Observation
        ↓
Input Validation
        ↓
Physics / Quality Control
        ↓
Multivariate Detection
        ↓
Temporal + Spatial Verification
        ↓
Weather Event vs Sensor Fault
        ↓
Explainable Decision
        ↓
Root Cause + Severity + Confidence
        ↓
Sensor Health
        ↓
Maintenance Recommendation
        ↓
Suggested Recovery (optional)
        ↓
Operator Dashboard
```

The most important demonstration is not simply that SkyGuard detects
anomalies.

It is that SkyGuard can demonstrate:

> **A value can be unusual without being faulty, and contextual evidence
> can help distinguish a genuine weather event from a sensor/data
> anomaly.**

------------------------------------------------------------------------

# 36. Reference Architecture Summary

``` text
                    SKYGUARD AI
                         │
                         ▼
              ┌────────────────────┐
              │ AWS Observations    │
              │ T / P / RH          │
              └─────────┬──────────┘
                        │
                        ▼
              ┌────────────────────┐
              │ Validate + Physics │
              │ QC / Fast Path     │
              └─────────┬──────────┘
                        │
                        ▼
              ┌────────────────────┐
              │ Isolation Forest   │
              │ Multivariate ML    │
              └─────────┬──────────┘
                        │
               ┌────────┴────────┐
               ▼                 ▼
       Temporal Evidence   Spatial Evidence
               │                 │
               └────────┬────────┘
                        ▼
              ┌────────────────────┐
              │ Event vs Fault     │
              │ Classification     │
              └─────────┬──────────┘
                        │
             ┌──────────┴──────────┐
             ▼                     ▼
       Root Cause              Severity /
       Classification           Confidence
             │                     │
             └──────────┬──────────┘
                        ▼
              ┌────────────────────┐
              │ SHAP Explanation   │
              └─────────┬──────────┘
                        ▼
              ┌────────────────────┐
              │ Sensor Health +    │
              │ Maintenance        │
              └─────────┬──────────┘
                        ▼
              ┌────────────────────┐
              │ Suggested Recovery │
              │ (Optional)         │
              └─────────┬──────────┘
                        ▼
              ┌────────────────────┐
              │ Streamlit / Plotly │
              │ Operator Dashboard │
              └────────────────────┘
```

This architecture is the baseline that implementation, testing,
documentation and presentation should remain consistent with.
