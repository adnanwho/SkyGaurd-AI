# Product Requirements Document (PRD)

# SkyGuard AI

**Project:** SkyGuard AI\
**SIH Problem Statement:** SIH26073 --- AI/ML-Based Intelligent Anomaly
Detection for Automatic Weather Stations (AWS)\
**Document Type:** Product Requirements Document\
**Version:** 1.0\
**Status:** Development Baseline\
**Primary Platform:** Local Python + Streamlit/Plotly prototype

------------------------------------------------------------------------

## 1. Product Overview

SkyGuard AI is a hybrid, explainable weather-observation quality-control
and sensor-health platform for Automatic Weather Stations (AWS).

The system analyzes three core meteorological observations:

-   Temperature (°C)
-   Atmospheric Pressure (hPa)
-   Relative Humidity (%)

Its primary purpose is to determine whether an observation is:

1.  Trustworthy/normal
2.  A genuine meteorological event
3.  A likely sensor or data anomaly

The central product differentiator is:

> **SkyGuard combines physical plausibility, multivariate machine
> learning, temporal behavior and neighboring-station evidence to
> distinguish sensor faults from genuine weather events.**

The product is designed as a local, executable prototype using simulated
and/or historical AWS observations. Live MQTT/Kafka ingestion, cloud
deployment, authentication, ESP32 deployment and other production
infrastructure are future-scope capabilities rather than initial MVP
requirements.

------------------------------------------------------------------------

## 2. Problem Statement

Automatic Weather Stations can produce abnormal observations because of:

-   Sensor malfunction
-   Communication failures
-   Calibration drift or bias
-   Frozen/stuck sensors
-   Sudden spikes
-   Missing or corrupted observations
-   Power or telemetry issues
-   Harsh environmental conditions
-   Cross-variable inconsistencies

A simple threshold-based system can flag unusual observations, but
**unusual does not necessarily mean faulty**.

For example:

-   One station reporting 55°C while nearby stations report
    approximately 31°C may indicate a local sensor fault.
-   Multiple nearby stations simultaneously reporting approximately 42°C
    may represent a genuine regional weather event.

SkyGuard therefore needs to combine multiple evidence sources instead of
relying on a single threshold or ML model.

------------------------------------------------------------------------

## 3. Product Goals

### 3.1 Primary Goals

SkyGuard must:

-   Ingest timestamped Temperature, Pressure and Relative Humidity
    observations.
-   Perform deterministic data-quality and physical-plausibility checks.
-   Detect multivariate anomalies using Isolation Forest.
-   Support temporal/seasonal anomaly analysis through an advanced LSTM
    Autoencoder module.
-   Use neighboring-station evidence when spatial information is
    available.
-   Distinguish isolated sensor faults from potentially genuine regional
    weather events.
-   Explain anomaly decisions using feature-level explainability.
-   Classify anomalies into a standardized fault taxonomy.
-   Assign severity and confidence.
-   Maintain a rolling sensor-health score.
-   Generate maintenance recommendations based on persistent degradation
    patterns.
-   Optionally generate suggested corrected/imputed values without
    overwriting original observations.
-   Present results through an operator-oriented Streamlit/Plotly
    dashboard.
-   Support row-by-row replay to demonstrate real-time behavior without
    requiring live infrastructure.
-   Produce measurable evaluation results using controlled anomaly
    injection.

### 3.2 Secondary Goals

The system should:

-   Support historical weather data for baseline creation.
-   Support synthetic AWS streams for controlled testing.
-   Be modular and station-independent.
-   Remain executable on ordinary local computing resources.
-   Preserve traceability of original observations and model outputs.
-   Provide a clear path toward multi-station deployment.

### 3.3 Non-Goals for the Initial MVP

The initial MVP does not require:

-   Production cloud infrastructure
-   Live IMD/AWS feeds
-   MQTT/Kafka production ingestion
-   WIS2.0 integration
-   ESP32 edge deployment
-   Authentication and role-based access
-   Production databases
-   Fully predictive maintenance ML
-   Exact prediction of sensor failure dates
-   Silent automatic replacement of official observations
-   Fabricated or assumed performance metrics

------------------------------------------------------------------------

## 4. Users and Stakeholders

### 4.1 Meteorologists / Weather Agencies

Need trustworthy AWS observations for:

-   Weather analysis
-   Forecasting workflows
-   Monitoring
-   Quality-controlled data products

### 4.2 AWS Maintenance Teams

Need:

-   Early identification of problematic sensors
-   Root-cause information
-   Sensor-health trends
-   Maintenance recommendations

### 4.3 Forecasting Systems

Need:

-   Cleaner observation streams
-   Reduced contamination from faulty measurements
-   Quality-controlled inputs for downstream forecasting

SkyGuard is a **data-quality system**, not itself a weather forecasting
model.

### 4.4 Researchers

Need:

-   Historical observations
-   Anomaly labels
-   Explainable anomaly decisions
-   Reproducible evaluation
-   Multi-station analysis

### 4.5 Operational Decision Makers

Need concise answers to:

-   Is this reading trustworthy?
-   Is this a sensor fault or a weather event?
-   What is the likely fault?
-   How severe is it?
-   How confident is the system?
-   Does the station require attention?

------------------------------------------------------------------------

## 5. Product Principles

### 5.1 Evidence Before Intervention

An unusual observation should not automatically be treated as a faulty
reading.

### 5.2 Preserve Original Data

Original observations must always be retained.

Suggested corrections must be stored separately and must never silently
overwrite source observations.

### 5.3 Rules + ML, Not Rules vs ML

Deterministic physics/data-quality rules provide fast validation while
ML detects patterns that rules may miss.

### 5.4 Explainability

Every flagged observation should have an understandable reason.

SHAP should be treated as feature contribution/explanation, not causal
proof.

### 5.5 Honest Capability Boundaries

The product must distinguish:

-   Core MVP
-   Advanced/optional modules
-   Future deployment

No unimplemented capability should be represented as operational.

------------------------------------------------------------------------

# 6. Canonical System Architecture

The canonical product flow is:

``` text
AWS Temperature + Pressure + Humidity
                    |
                    v
             Data + Physics QC
                    |
                    v
             Isolation Forest
                    |
                    v
        Temporal + Spatial Validation
                    |
                    v
       Weather Event vs Sensor Fault
                    |
                    v
             SHAP Explanation
                    |
                    v
       Root Cause + Severity + Confidence
                    |
                    v
              Sensor Health
                    |
                    v
       Suggested Correction / Recovery
                    |
                    v
                Dashboard
```

The operational reasoning sequence is:

> **Validate → Detect → Verify → Explain → Diagnose → Recover**

------------------------------------------------------------------------

# 7. Functional Requirements

## FR-01: Data Ingestion

The system shall accept timestamped AWS observations containing at
minimum:

``` text
station_id
timestamp
temperature
pressure
humidity
```

Optional metadata may include:

``` text
latitude
longitude
elevation
```

The prototype shall support local data sources such as CSV/Parquet and
simulated streams.

### Acceptance Criteria

-   A documented input schema exists.
-   Valid observations can be loaded into the pipeline.
-   Invalid/malformed observations are identified rather than silently
    accepted.
-   Station and timestamp information remain attached to every processed
    observation.

------------------------------------------------------------------------

## FR-02: Preprocessing and Data Quality Checks

The preprocessing layer shall identify:

-   Missing values
-   Duplicate observations
-   Invalid timestamps
-   Timestamp gaps
-   Persistence/flatline behavior
-   Abrupt changes
-   Basic data-format problems

The preprocessing output shall be suitable for physics checks and ML
feature generation.

### Acceptance Criteria

-   Missing observations are explicitly represented.
-   Duplicate timestamps can be identified.
-   Time-series ordering is deterministic.
-   Preprocessing does not silently alter source observations.

------------------------------------------------------------------------

## FR-03: Physics-Based Quality Control

The system shall perform fast deterministic checks including:

-   Physical range checks
-   Step/rate checks
-   Persistence checks
-   Thermodynamic consistency checks

The system may use Magnus-Tetens-derived dew-point calculations as part
of humidity/temperature consistency validation.

### Fast-Path Behavior

Clearly impossible observations should be capable of being flagged
immediately without requiring deep-learning inference.

### Acceptance Criteria

-   Each rule returns a machine-readable result.
-   Rule failures identify the violated condition.
-   Rule results are available to downstream scoring/classification.
-   Original observations remain unchanged.

------------------------------------------------------------------------

## FR-04: Multivariate Anomaly Detection

Isolation Forest shall serve as the primary unsupervised multivariate
anomaly detector.

It shall analyze combinations of Temperature, Pressure, Humidity and
relevant derived features.

The objective is to detect observations that may be individually
plausible but jointly inconsistent.

Example:

``` text
Temperature = unusual
Humidity    = unusual
Pressure    = inconsistent
```

### Acceptance Criteria

-   A baseline dataset can be used to fit the model.
-   New observations receive an anomaly score.
-   The result can be integrated with rule-based evidence.
-   Model outputs are reproducible when deterministic seeds are used
    where appropriate.

------------------------------------------------------------------------

## FR-05: Temporal and Seasonal Analysis

An advanced temporal module shall support detection of deviations from
learned temporal behavior.

The planned advanced implementation is an LSTM Autoencoder.

Its purpose is to learn normal temporal/seasonal behavior and identify
sequence deviations.

Example:

``` text
31.0 → 31.1 → 31.2 → 31.3 → 55.0 → 31.4
```

The LSTM Autoencoder is an advanced module and must not be represented
as implemented unless the actual project implementation contains and
validates it.

### Acceptance Criteria

For the advanced module:

-   A sequence can be constructed from historical observations.
-   A temporal model can learn a baseline of normal behavior.
-   Reconstruction error can be used as temporal anomaly evidence.
-   The module can be independently enabled/disabled.

------------------------------------------------------------------------

## FR-06: Spatial Consistency

When neighboring station information is available, SkyGuard shall
compare observations across nearby AWS stations.

Example:

``` text
AWS-01 = 55.0°C
AWS-02 = 31.0°C
AWS-03 = 31.4°C
AWS-04 = 30.8°C
```

This pattern suggests a likely local sensor anomaly.

Conversely:

``` text
AWS-01 = 42.0°C
AWS-02 = 41.7°C
AWS-03 = 42.2°C
AWS-04 = 41.9°C
```

suggests a potentially genuine regional event.

### Acceptance Criteria

-   Neighboring observations can be associated with a target station.
-   Consensus/deviation evidence is calculated.
-   Spatial evidence affects the event-vs-fault decision.
-   The system can demonstrate both isolated-fault and regional-event
    scenarios.

------------------------------------------------------------------------

## FR-07: Weather Event vs Sensor Fault Decision

The system shall combine evidence from:

-   Physics QC
-   Isolation Forest
-   Temporal analysis when available
-   Spatial consistency
-   Persistence/trajectory patterns
-   Missing/communication behavior

The decision layer shall distinguish, where evidence supports it,
between:

-   Genuine weather event
-   Likely sensor/data anomaly
-   Uncertain/insufficient evidence

### Acceptance Criteria

A multi-station demo shall show that a synchronized change across
neighboring stations is treated differently from an isolated station
anomaly.

The system must not claim certainty beyond the available evidence.

------------------------------------------------------------------------

## FR-08: Root-Cause Classification

SkyGuard shall use the following standardized taxonomy:

1.  **Spike**
2.  **Frozen/Stuck**
3.  **Drift/Bias**
4.  **Communication/Missing**

### Classification Examples

  Pattern                        Likely Root Cause
  ------------------------------ -----------------------
  Sudden isolated jump           Spike
  Repeated identical value       Frozen/Stuck
  Gradual persistent deviation   Drift/Bias
  Missing/gapped telemetry       Communication/Missing

The taxonomy must remain consistent across code, dashboard,
documentation and presentation.

------------------------------------------------------------------------

## FR-09: Severity Scoring

Each detected anomaly should receive:

-   Low
-   Medium
-   High

Severity should be derived from evidence such as:

-   Magnitude of deviation
-   Persistence
-   Anomaly evidence
-   Rule violations
-   Spatial context
-   Potential operational impact

No arbitrary numerical performance claim should be presented as measured
accuracy.

------------------------------------------------------------------------

## FR-10: Confidence Scoring

Each anomaly should receive a confidence score representing the strength
of the combined evidence.

The confidence score shall be clearly distinguished from:

-   Model accuracy
-   Precision
-   Recall
-   F1-score

Confidence values must not be fabricated for presentation purposes.

------------------------------------------------------------------------

## FR-11: Explainability

SHAP shall provide feature-level attribution for the anomaly decision
where applicable.

Example:

``` text
Anomaly detected

Temperature  → High contribution
Humidity     → Medium contribution
Pressure     → Low contribution
```

The dashboard should translate technical attribution into
operator-readable reasoning.

### Acceptance Criteria

-   A flagged observation can expose feature contributions.
-   The UI identifies the major contributing parameters.
-   Explanation text is understandable without requiring ML expertise.
-   Explanations do not claim causal certainty.

------------------------------------------------------------------------

## FR-12: Sensor Health

SkyGuard shall maintain a rolling sensor-health score based on factors
such as:

-   Anomaly frequency
-   Persistent anomalies
-   Drift indicators
-   Recent behavior
-   Fault history

The first implementation should be a transparent trend-based health
score rather than a claimed predictive-maintenance model.

### Acceptance Criteria

-   Health can be displayed over time.
-   Repeated faults can lower health.
-   Recovery/healthy behavior can be reflected appropriately.
-   Health status can be categorized for operators.

------------------------------------------------------------------------

## FR-13: Maintenance Recommendations

The system shall convert sustained degradation signals into actionable
recommendations.

Examples:

  Observation Pattern               Recommendation
  --------------------------------- -----------------------------------------
  Increasing drift                  Inspect / recalibrate sensor
  Repeated frozen readings          Inspect sensing element / firmware path
  Repeated communication gaps       Inspect power/network/telemetry path
  High anomaly frequency            Inspect sensor health
  Low health + rising fault trend   Maintenance recommended

The system shall not claim an exact future failure date without
validated predictive-maintenance data and a corresponding model.

------------------------------------------------------------------------

## FR-14: Suggested Correction / Data Recovery

For suitable anomalies, SkyGuard may generate a suggested corrected or
imputed value using available temporal, spatial or model-based evidence.

The product shall preserve:

``` text
original_value
suggested_value
```

The suggested value must be presented as a proposal for validation, not
as an automatically trusted replacement.

### Acceptance Criteria

-   Original observation is preserved.
-   Suggested value is stored separately.
-   The source/evidence for the suggested value can be identified.
-   The feature is only presented as active when implemented and
    validated.

------------------------------------------------------------------------

## FR-15: Real-Time Replay

The prototype shall support row-by-row replay to simulate a streaming
system.

For each observation:

``` text
validate
  ↓
create features
  ↓
run rules
  ↓
run ML
  ↓
calculate score
  ↓
explain
  ↓
classify
  ↓
update dashboard
```

A short delay may be used to make the replay visually demonstrate
real-time processing.

### Acceptance Criteria

-   Healthy observations appear progressively.
-   Injected anomalies trigger alerts during replay.
-   Charts update as observations arrive.
-   Processing latency can be measured.

------------------------------------------------------------------------

## FR-16: Dashboard

The dashboard shall be implemented using Streamlit and Plotly.

### Required Dashboard Components

#### Station Overview

-   Temperature
-   Pressure
-   Humidity
-   Current status
-   Sensor-health status

#### Time Series

-   Historical/current trends
-   Anomaly markers
-   Parameter selection

#### Anomaly Table

At minimum:

-   Timestamp
-   Station
-   Parameter/context
-   Anomaly score
-   Confidence
-   Root cause
-   Severity

#### Explanation Panel

-   SHAP contribution
-   Plain-English reasoning
-   Evidence summary

#### Spatial Panel

-   Target station
-   Neighboring stations
-   Consensus/deviation information
-   Weather-event vs sensor-fault interpretation

#### Health Panel

-   Current health
-   Historical health trend
-   Maintenance recommendation

#### Recovery Panel

When implemented:

-   Original value
-   Suggested value
-   Supporting evidence
-   Validation status

### UX Principle

The dashboard should answer operator decision questions first and hide
unnecessary ML jargon.

------------------------------------------------------------------------

# 8. Data Requirements

## 8.1 Core Schema

Every observation should contain:

``` text
station_id
timestamp
temperature
pressure
humidity
```

Every processed result should expose a predictable result object
containing:

``` text
station_id
timestamp
status
anomaly_score
confidence
root_cause
severity
explanation
health_score
maintenance_recommendation
original_values
suggested_values
```

`suggested_values` may be unavailable when the recovery module is
disabled.

------------------------------------------------------------------------

## 8.2 Historical Data

Historical meteorological observations may be used to establish normal
patterns and realistic baselines.

The intended major source is:

-   NOAA/NCEI Integrated Surface Database (ISD)

Potential supporting sources include:

-   NOAA GSOD
-   NOAA Climate Data Online
-   ECMWF ERA5

The prototype must clearly distinguish external historical data from
simulated data.

------------------------------------------------------------------------

## 8.3 Simulated Data

The simulator shall generate realistic time-series behavior suitable
for:

-   Normal operation
-   Multi-station behavior
-   Seasonal/temporal patterns
-   Controlled fault injection
-   Regional weather-event scenarios

------------------------------------------------------------------------

# 9. Anomaly Injection Requirements

Because labeled real-world sensor faults are difficult to obtain, the
evaluation dataset shall include controlled anomaly injection.

## 9.1 Spike

Example:

``` text
31.2 → 31.4 → 55.0 → 31.3
```

Expected label:

``` text
Spike
```

## 9.2 Frozen/Stuck

Example:

``` text
31.2 → 31.2 → 31.2 → 31.2 → 31.2
```

Expected label:

``` text
Frozen/Stuck
```

## 9.3 Drift/Bias

Example:

``` text
31.0 → 31.2 → 31.5 → 31.8 → 32.1
```

Expected label:

``` text
Drift/Bias
```

## 9.4 Communication/Missing

Example:

``` text
31.2
31.3
NULL
NULL
31.4
```

Expected label:

``` text
Communication/Missing
```

## 9.5 Cross-Variable Inconsistency

The injector should support cases where individual values may appear
plausible but their combination is inconsistent.

## 9.6 Regional Event

Multiple neighboring stations should be modified together to represent a
genuine regional event.

## 9.7 Isolated Station Fault

Only one station should be modified while neighboring stations remain
normal.

These scenarios are essential for testing false-alarm minimization and
event-vs-fault discrimination.

------------------------------------------------------------------------

# 10. Evaluation Requirements

The evaluation dataset shall contain:

-   Clean observations
-   Injected anomalies
-   Known ground-truth labels
-   Multiple fault types
-   Multi-station scenarios
-   Normal seasonal extremes

## 10.1 Required Metrics

The system should eventually report:

-   Precision
-   Recall
-   F1-score
-   False-positive rate / false alarm rate
-   False-negative rate
-   Detection latency
-   Root-cause classification accuracy

Optional:

-   Confidence calibration
-   Correction quality

## 10.2 Critical Test Scenarios

The evaluation suite shall include:

1.  Large spike on one station
2.  Subtle drift over many readings
3.  Frozen sensor
4.  Communication gap
5.  Individually plausible but multivariate-inconsistent values
6.  Regional weather event
7.  Single-station extreme value with normal neighbors
8.  Missing values around an anomaly
9.  Repeated faults causing declining sensor health
10. Normal seasonal extremes that should not become false positives

## 10.3 Reporting Rule

No performance percentage may be placed in the final product, dashboard
or presentation unless it comes from an actual reproducible evaluation
run.

------------------------------------------------------------------------

# 11. Non-Functional Requirements

## NFR-01: Performance

The prototype should process observations fast enough to support
row-by-row real-time replay.

Processing latency shall be measured rather than assumed.

## NFR-02: Reliability

The pipeline should fail explicitly on malformed inputs rather than
silently producing misleading results.

## NFR-03: Reproducibility

Synthetic experiments should use deterministic seeds where
reproducibility is useful.

## NFR-04: Data Integrity

Original observations must be preserved.

Model outputs and anomaly metadata should be retained for traceability.

## NFR-05: Offline Operation

The main prototype should be capable of running locally without
requiring third-party cloud APIs at runtime.

## NFR-06: Modularity

Components should be independently testable and replaceable.

## NFR-07: Scalability

The processing architecture should be station-independent and structured
so that a single-station prototype can evolve toward a larger station
network.

## NFR-08: Explainability

Flagged observations should expose understandable evidence.

------------------------------------------------------------------------

# 12. Recommended Technical Stack

  Category                  Technology
  ------------------------- ------------------
  Language                  Python 3.10+
  Numerical Computing       NumPy
  Data Processing           Pandas
  ML                        Scikit-learn
  Primary Detector          Isolation Forest
  Deep Learning             TensorFlow/Keras
  Advanced Temporal Model   LSTM Autoencoder
  Explainability            SHAP
  Visualization             Plotly
  Dashboard                 Streamlit
  Storage                   CSV / Parquet
  Model Persistence         Joblib
  Testing                   Pytest

Physics/QC logic should use custom Python implementations aligned with
the project's selected meteorological quality-control guidance.

------------------------------------------------------------------------

# 13. Software Architecture

Recommended repository structure:

``` text
skyguard-ai/
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── simulated/
│
├── models/
│
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── schemas.py
│   ├── data_simulator.py
│   ├── historical_adapter.py
│   ├── anomaly_injector.py
│   ├── preprocessing.py
│   ├── feature_engineering.py
│   ├── rule_checks.py
│   ├── isolation_forest_model.py
│   ├── spatial_consistency.py
│   ├── lstm_autoencoder.py
│   ├── event_classifier.py
│   ├── explainability.py
│   ├── scoring.py
│   ├── sensor_health.py
│   ├── maintenance.py
│   └── pipeline.py
│
├── dashboard/
│   ├── __init__.py
│   └── app.py
│
├── tests/
│   ├── test_rules.py
│   ├── test_features.py
│   ├── test_anomaly_detection.py
│   ├── test_spatial.py
│   ├── test_classification.py
│   ├── test_health.py
│   └── test_pipeline.py
│
├── examples/
│   ├── demo_spike.py
│   ├── demo_weather_event.py
│   └── sample_input.csv
│
├── notebooks/
│   └── exploration.ipynb
│
├── reports/
│   ├── evaluation/
│   └── figures/
│
├── requirements.txt
├── README.md
├── run.py
└── .gitignore
```

`src/pipeline.py` should act as the central orchestration layer.

------------------------------------------------------------------------

# 14. Processing Contract

Every processed observation should return a predictable object.

Example:

``` json
{
  "station_id": "AWS-01",
  "timestamp": "2026-01-01T12:00:00",
  "status": "ANOMALY",
  "anomaly_score": 0.0,
  "confidence": 0.0,
  "root_cause": "Spike",
  "severity": "High",
  "explanation": "Temperature contributed strongly to the anomaly.",
  "health_score": 0.0,
  "maintenance_recommendation": "Inspect / recalibrate sensor",
  "original_values": {},
  "suggested_values": {}
}
```

The numerical values above are structural examples only and must not be
interpreted as measured project results.

------------------------------------------------------------------------

# 15. Development Phases

## Phase 1 --- Core MVP

Must build:

``` text
Simulator
   ↓
Anomaly Injector
   ↓
Preprocessing
   ↓
Physics QC
   ↓
Isolation Forest
   ↓
Basic Classification
   ↓
Dashboard
```

### Exit Criteria

-   Data can be generated/loaded.
-   Faults can be injected.
-   Physics rules work.
-   Isolation Forest produces anomaly outputs.
-   Basic fault classification works.
-   Dashboard displays the results.
-   Evaluation can be executed.

------------------------------------------------------------------------

## Phase 2 --- Intelligence Layer

Build:

-   Spatial validation
-   Weather-event vs sensor-fault logic
-   SHAP explanations
-   Severity/confidence
-   Sensor health
-   Maintenance recommendations

### Exit Criteria

-   Isolated faults and regional events can be demonstrated.
-   Flagged observations have explanations.
-   Sensor health responds to repeated anomalies.
-   Maintenance recommendations are generated from defined rules.

------------------------------------------------------------------------

## Phase 3 --- Advanced Modules

Build:

-   LSTM Autoencoder
-   Advanced temporal/seasonal analysis
-   Suggested correction/reconstruction
-   More advanced recovery logic

### Exit Criteria

Advanced modules are validated independently and are only exposed as
active capabilities when their implementation and evaluation are
complete.

------------------------------------------------------------------------

## Phase 4 --- Future Deployment

Potential future work:

-   MQTT
-   Kafka
-   WIS2.0 integration
-   Cloud deployment
-   Authentication
-   Production database
-   ESP32/edge deployment
-   Larger AWS network deployment

These are future deployment capabilities and must not be represented as
implemented in the MVP.

------------------------------------------------------------------------

# 16. Team Workstreams

A small team can work in parallel using the following workstreams.

  -----------------------------------------------------------------------
  Workstream              Responsibility          Handoff
  ----------------------- ----------------------- -----------------------
  Data                    Simulator, historical   Schema + datasets
                          adapter, anomaly        
                          injection               

  ML                      Preprocessing,          Model + metrics
                          Isolation Forest,       
                          evaluation              

  Intelligence            Spatial, event          Decision modules
                          decision, health,       
                          maintenance             

  XAI                     SHAP + explanation      Explanation payload
                          templates               

  Frontend                Streamlit + Plotly      Dashboard consuming
                                                  final output schema

  QA / Documentation      Tests, README, PPT,     Release checklist
                          demo                    
  -----------------------------------------------------------------------

All workstreams must follow the same processing schema and canonical
architecture.

------------------------------------------------------------------------

# 17. Security and Data Integrity

## Prototype

-   Prefer local/offline execution.
-   Avoid requiring cloud APIs at runtime.
-   Preserve original observations.
-   Store anomaly metadata and model outputs for traceability.
-   Use reproducible seeds where appropriate.

## Production Future Scope

Production deployment should eventually consider:

-   Authenticated ingestion
-   Encryption in transit and at rest
-   Role-based access
-   Audit logging
-   Backups/disaster recovery
-   Secure model/version management

These controls are not MVP requirements unless actually implemented and
tested.

------------------------------------------------------------------------

# 18. User Stories

### US-01 --- Detect Fault

> As an AWS operator, I want abnormal observations flagged automatically
> so that I can investigate faulty sensors.

### US-02 --- Understand the Alert

> As an operator, I want to know why an observation was flagged so that
> I can make an informed decision.

### US-03 --- Distinguish Weather from Fault

> As a meteorologist, I want neighboring stations considered so that a
> genuine regional event is not incorrectly treated as a sensor failure.

### US-04 --- Identify Root Cause

> As a maintenance engineer, I want anomalies categorized as Spike,
> Frozen/Stuck, Drift/Bias or Communication/Missing so that I know what
> type of problem to investigate.

### US-05 --- Monitor Sensor Health

> As a maintenance team member, I want a health trend so that recurring
> anomalies and degradation become visible.

### US-06 --- Recover Missing/Corrupt Data

> As a data operator, I want a suggested replacement value while
> preserving the original observation so that recovery can be reviewed
> safely.

### US-07 --- Replay Real-Time Behavior

> As a hackathon evaluator, I want to see observations processed
> sequentially so that the system's real-time behavior can be
> demonstrated without live infrastructure.

------------------------------------------------------------------------

# 19. Acceptance Criteria for MVP

The SkyGuard MVP is considered complete only when:

-   [ ] A fresh environment can install dependencies.
-   [ ] Documented input data can be loaded.
-   [ ] Synthetic data can be generated.
-   [ ] Controlled anomalies can be injected.
-   [ ] Physics/data-quality checks work.
-   [ ] Isolation Forest is trained and used for anomaly detection.
-   [ ] Basic root-cause classification works.
-   [ ] Evaluation metrics can be generated from labeled scenarios.
-   [ ] Spatial validation can demonstrate isolated-fault vs
    regional-event behavior.
-   [ ] SHAP explanation is available if claimed in the MVP.
-   [ ] Severity and confidence are calculated.
-   [ ] Sensor-health monitoring works.
-   [ ] Maintenance recommendations work.
-   [ ] Streamlit dashboard displays the required information.
-   [ ] Real-time replay works.
-   [ ] Original observations are preserved.
-   [ ] Tests cover core pipeline behavior.
-   [ ] README contains installation and execution instructions.
-   [ ] No unimplemented feature is presented as implemented.
-   [ ] No fabricated performance number appears in the product or
    presentation.

------------------------------------------------------------------------

# 20. Definition of Done

A release candidate is ready when:

1.  The application runs in a clean environment.
2.  The end-to-end pipeline processes simulated or historical data.
3.  Known injected faults produce traceable outputs.
4.  Regional weather scenarios are not automatically treated as isolated
    sensor faults when spatial evidence supports the event
    interpretation.
5.  Operators can understand why an observation was flagged.
6.  Root cause and severity are visible.
7.  Sensor health and maintenance recommendations are visible.
8.  Original values remain intact.
9.  Evaluation metrics are reproducible.
10. Dashboard replay works reliably.
11. Tests pass.
12. Documentation matches actual implementation.
13. The PPT/demo uses only verified capabilities.

------------------------------------------------------------------------

# 21. Product Metrics

The product should measure:

### Detection

-   Precision
-   Recall
-   F1-score
-   False-positive rate
-   False-negative rate

### Operational

-   Detection latency
-   Processing latency per observation
-   Replay stability

### Diagnosis

-   Root-cause classification accuracy

### Recovery --- Optional

-   Suggested-value error
-   Reconstruction quality
-   Recovery acceptance rate, if operator validation data becomes
    available

### Health

-   Health-score trend
-   Fault-frequency trend

No metric should be reported without a corresponding evaluation
procedure and actual measured result.

------------------------------------------------------------------------

# 22. Demo Requirements

The preferred demonstration sequence is:

1.  Start with healthy observations.
2.  Show live/replay time-series charts.
3.  Introduce a spike.
4.  Show the alert.
5.  Open the explanation.
6.  Show root cause and severity.
7.  Introduce a frozen sensor.
8.  Show health degradation.
9.  Demonstrate neighboring-station evidence.
10. Trigger a regional event.
11. Show that synchronized neighboring behavior changes the
    interpretation.
12. Show suggested recovery only if implemented.
13. Finish with evaluation metrics and processing latency.

The demo should tell one coherent story:

> **A value looks abnormal → SkyGuard validates it → detects it → checks
> context → determines whether it is a weather event or sensor fault →
> explains why → diagnoses the fault → assesses sensor health →
> optionally suggests recovery.**

------------------------------------------------------------------------

# 23. Product Risks and Mitigations

  -----------------------------------------------------------------------
  Risk                                Mitigation
  ----------------------------------- -----------------------------------
  False positives                     Combine physics, ML, temporal and
                                      spatial evidence

  Missing/noisy data                  Explicit preprocessing and QC

  Rare faults                         Controlled anomaly injection

  Genuine extreme weather flagged as  Neighboring-station validation
  faulty                              

  Incorrect correction                Preserve original value and require
                                      validation

  Model drift                         Periodic evaluation/retraining

  Lack of labeled faults              Synthetic controlled ground truth

  Overclaiming capabilities           Explicit MVP/advanced/future
                                      boundaries

  Heavy computation                   Rules-first fast path and
                                      lightweight local models
  -----------------------------------------------------------------------

------------------------------------------------------------------------

# 24. Presentation Consistency Requirements

All project artifacts must describe the same SkyGuard architecture.

The presentation should use:

> **Validate → Detect → Verify → Explain → Diagnose → Recover**

The project should consistently use:

> **Spike \| Frozen/Stuck \| Drift/Bias \| Communication/Missing**

The project should consistently use:

> **Suggested Correction / Data Recovery**

instead of "Self-Healing" for the normal MVP terminology.

The presentation must not introduce an unrelated:

-   3-agent architecture
-   18B parameter claim
-   70B+ model comparison
-   Anomaly Knowledge Base architecture
-   Agentic architecture

unless the actual product architecture is intentionally changed and
implemented.

------------------------------------------------------------------------

# 25. Research and Evidence Requirements

The product documentation and presentation should map references to
actual system components.

Suggested mapping:

``` text
WMO guidance
    → Physics / Quality Control

Meteorological ML / Autoencoder research
    → Temporal anomaly detection

SHAP research
    → Explainability

Spatial/temporal meteorological QC research
    → Neighbor validation

NOAA/NCEI
    → Historical observations
```

NotebookLM should not be treated as a formal research reference.

------------------------------------------------------------------------

# 26. Future Product Roadmap

## Near Term

-   Complete core data pipeline
-   Complete physics QC
-   Train/evaluate Isolation Forest
-   Implement spatial validation
-   Implement SHAP
-   Implement health and maintenance logic
-   Complete dashboard
-   Build automated test suite
-   Produce reproducible evaluation report

## Advanced

-   LSTM Autoencoder
-   Advanced temporal/seasonal intelligence
-   Model-based suggested correction
-   Stronger recovery validation
-   Improved multi-station analysis

## Production

-   Live AWS/IMD-authorized feeds
-   MQTT/Kafka/WIS2.0 adapters
-   Cloud deployment
-   Authentication
-   Persistent production storage
-   Edge/ESP32 optimization
-   Larger AWS network

------------------------------------------------------------------------

# 27. Final Product Definition

SkyGuard AI is a **hybrid AI/ML quality-control and sensor-health system
for Automatic Weather Stations**.

It does not simply ask:

> "Is this value unusual?"

It asks:

> **"Is this observation physically plausible, statistically/temporally
> consistent, spatially supported, and therefore more likely to
> represent a real weather event or a sensor/data fault?"**

The complete product value chain is:

``` text
Raw AWS Observations
        ↓
Quality & Physics Validation
        ↓
Multivariate Anomaly Detection
        ↓
Temporal / Spatial Verification
        ↓
Weather Event vs Sensor Fault
        ↓
Explainable Diagnosis
        ↓
Severity + Confidence
        ↓
Sensor Health
        ↓
Maintenance Recommendation
        ↓
Suggested Recovery (when validated)
        ↓
Operator Dashboard
```

The MVP succeeds when it can execute this chain reliably on controlled
or historical AWS data, demonstrate known anomaly scenarios, distinguish
isolated faults from regional behavior, provide understandable
explanations, and produce reproducible evaluation evidence without
overstating capabilities.
