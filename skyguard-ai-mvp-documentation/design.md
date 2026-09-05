# SkyGuard AI --- Product & UX Design Specification

**Project:** SkyGuard AI\
**SIH Problem Statement:** SIH26073 --- AI/ML-Based Intelligent Anomaly
Detection for Automatic Weather Stations (AWS)\
**Design Version:** 1.0\
**Status:** Design Baseline\
**Primary UI:** Streamlit + Plotly\
**Design Goal:** Operator-first, technically credible, explainable
weather-observation quality control

------------------------------------------------------------------------

# 1. Design Overview

SkyGuard AI is designed as an **operator-facing weather observation
intelligence console**, not as a generic AI dashboard.

The interface must make the system's reasoning understandable:

> **What happened → Is it real weather or a sensor problem → Why does
> SkyGuard think that → How serious is it → What should the operator
> do?**

The design should prioritize:

1.  Current station state
2.  Immediate anomaly visibility
3.  Contextual evidence
4.  Root-cause diagnosis
5.  Sensor health
6.  Suggested recovery
7.  Technical evidence on demand

The UI should hide unnecessary ML complexity while still exposing enough
evidence for technical users to validate the decision.

------------------------------------------------------------------------

# 2. Core Design Principle

The central UX principle is:

> **An unusual observation is not automatically a faulty observation.**

The interface must therefore avoid presenting every anomaly as a
confirmed sensor failure.

Instead, the visual hierarchy should communicate:

``` text
Observation
     ↓
Validation
     ↓
Anomaly Detection
     ↓
Context / Evidence
     ↓
Event vs Fault
     ↓
Diagnosis
     ↓
Action
```

------------------------------------------------------------------------

# 3. Primary User Questions

The dashboard should answer these questions in order.

### Q1 --- What is happening right now?

Show:

-   Current Temperature
-   Current Pressure
-   Current Humidity
-   Station status
-   Latest anomaly status

### Q2 --- Is something abnormal?

Show:

-   Alert state
-   Anomaly score
-   Recent anomaly count
-   Affected parameter

### Q3 --- Is it actually a sensor fault?

Show:

-   Physics/QC evidence
-   Temporal evidence
-   Neighboring-station evidence
-   Event-vs-fault interpretation

### Q4 --- What is the likely problem?

Show:

-   Spike
-   Frozen/Stuck
-   Drift/Bias
-   Communication/Missing

### Q5 --- How serious is it?

Show:

-   Severity
-   Confidence
-   Sensor health

### Q6 --- What should happen next?

Show:

-   Maintenance recommendation
-   Suggested correction/data recovery when available

------------------------------------------------------------------------

# 4. Design Hierarchy

The interface should use the following information hierarchy:

``` text
LEVEL 1 — Operational State
    ↓
LEVEL 2 — Active Alerts
    ↓
LEVEL 3 — Time-Series Evidence
    ↓
LEVEL 4 — Event/Fault Context
    ↓
LEVEL 5 — Diagnosis
    ↓
LEVEL 6 — Explanation
    ↓
LEVEL 7 — Recovery / Maintenance
    ↓
LEVEL 8 — Technical Details
```

A user should be able to understand the current situation without
opening every technical panel.

------------------------------------------------------------------------

# 5. Application Layout

Recommended desktop layout:

``` text
┌──────────────────────────────────────────────────────────────────┐
│ SKYGUARD AI                              Station: AWS-01   ● LIVE │
│ Intelligent AWS Observation Quality Control                      │
├──────────────────────────────────────────────────────────────────┤
│                                                                  │
│ ┌───────────┐ ┌───────────┐ ┌───────────┐ ┌───────────────────┐ │
│ │ Temp      │ │ Pressure  │ │ Humidity  │ │ Sensor Health     │ │
│ │ 31.4 °C   │ │ 1008 hPa  │ │ 62 %      │ │ 87 / 100          │ │
│ │ Normal    │ │ Normal    │ │ Normal    │ │ Healthy           │ │
│ └───────────┘ └───────────┘ └───────────┘ └───────────────────┘ │
│                                                                  │
│ ┌────────────────────────────────┐ ┌───────────────────────────┐ │
│ │ LIVE OBSERVATION TRENDS        │ │ ALERT / EVENT STATUS      │ │
│ │                                │ │                           │ │
│ │ Temperature                    │ │ ● No active fault        │ │
│ │ Pressure                       │ │                           │ │
│ │ Humidity                       │ │ Recent anomalies: 2       │ │
│ │                                │ │                           │ │
│ └────────────────────────────────┘ └───────────────────────────┘ │
│                                                                  │
│ ┌──────────────────────────────────────────────────────────────┐ │
│ │ SELECTED ANOMALY                                             │ │
│ │                                                              │ │
│ │ Likely Sensor Fault   | Spike   | High   | 94% confidence   │ │
│ │                                                              │ │
│ │ Evidence / Explanation / SHAP / Spatial Comparison           │ │
│ └──────────────────────────────────────────────────────────────┘ │
│                                                                  │
│ ┌──────────────────────────┐ ┌────────────────────────────────┐ │
│ │ SENSOR HEALTH            │ │ MAINTENANCE / RECOVERY         │ │
│ │ Trend + status            │ │ Recommendation                │ │
│ │                           │ │ Original vs suggested value   │ │
│ └──────────────────────────┘ └────────────────────────────────┘ │
└──────────────────────────────────────────────────────────────────┘
```

The exact implementation may adapt this structure to Streamlit
constraints.

------------------------------------------------------------------------

# 6. Visual Language

## 6.1 Overall Style

The design should feel like a **professional meteorological monitoring
console** rather than a consumer weather application.

Desired characteristics:

-   Dense but readable
-   Technical
-   Calm
-   Trustworthy
-   High information value
-   Minimal decorative content
-   Strong visual hierarchy
-   Consistent status indicators

The dashboard should prioritize function over visual effects.

------------------------------------------------------------------------

# 7. Color Semantics

Colors should communicate system state consistently.

Recommended semantic mapping:

  State              Meaning
  ------------------ ------------------------------------------
  Normal / Healthy   Safe operating state
  Warning            Observation or health requires attention
  Anomaly            Abnormal observation detected
  Critical           High-priority issue
  Unknown            Insufficient evidence
  Informational      Context/evidence only

Color should never be the only indicator.

Every important state should also contain:

-   Text label
-   Icon or symbol
-   Numerical/contextual information

This supports accessibility and prevents ambiguity.

------------------------------------------------------------------------

# 8. Typography

Typography should follow a simple hierarchy.

### Application Title

Large, bold, high contrast.

### Section Titles

Medium/large and clearly separated.

### Metric Values

Large enough to scan quickly.

### Supporting Labels

Compact and muted.

### Technical Details

Smaller text may be used inside expandable sections.

The interface should avoid excessive font styles.

------------------------------------------------------------------------

# 9. Header Design

The header should establish system identity and current operating state.

Recommended:

``` text
SKYGUARD AI
Intelligent AWS Observation Quality Control

Station: AWS-01
Mode: REAL-TIME REPLAY
System: ONLINE
```

The header should also expose:

-   Selected station
-   Current processing mode
-   Dataset/replay state
-   Optional last-update timestamp

------------------------------------------------------------------------

# 10. Station Selector

The user should be able to select a station when multi-station data is
available.

Example:

``` text
Station
[ AWS-01 ▼ ]
```

Optional:

``` text
Region
[ North Zone ▼ ]

Time Window
[ Last 24 Hours ▼ ]
```

Station selection should update all relevant panels consistently.

------------------------------------------------------------------------

# 11. Top Metric Cards

The first content layer should contain the current observation state.

Recommended cards:

### Temperature

``` text
TEMPERATURE
31.4 °C
NORMAL
```

### Pressure

``` text
PRESSURE
1008.2 hPa
NORMAL
```

### Humidity

``` text
HUMIDITY
61 %
NORMAL
```

### Sensor Health

``` text
SENSOR HEALTH
87 / 100
HEALTHY
```

Cards should support quick scanning.

Avoid filling cards with model jargon.

------------------------------------------------------------------------

# 12. Live Observation Chart

The primary chart should show time-series observations.

## Required Features

-   Temperature
-   Pressure
-   Humidity
-   Time axis
-   Anomaly markers
-   Selected time range
-   Hover information
-   Clear legend

The user should be able to identify:

``` text
Normal trend
     vs
Abnormal point
     vs
Persistent degradation
```

Anomaly markers should connect visually to the corresponding anomaly
record.

------------------------------------------------------------------------

# 13. Parameter Selection

The chart should allow:

``` text
[ Temperature ]
[ Pressure ]
[ Humidity ]
[ All ]
```

When "All" is selected, the implementation should avoid visually
misleading comparisons caused by different physical scales.

Separate axes or separate charts may be used where necessary.

------------------------------------------------------------------------

# 14. Alert Panel

The alert panel should communicate the current state immediately.

Example normal state:

``` text
SYSTEM STATUS
● No active sensor fault

Last anomaly:
14:32 — Temperature spike
Resolved / under review
```

Example fault state:

``` text
HIGH PRIORITY ALERT

Temperature anomaly detected

Likely cause:
SPIKE

Severity:
HIGH

Confidence:
94%

Action:
Inspect / recalibrate sensor
```

The UI should distinguish:

-   Detection
-   Diagnosis
-   Recommendation

A detected anomaly should not automatically be displayed as a confirmed
physical failure.

------------------------------------------------------------------------

# 15. Anomaly Table

The anomaly table is the primary investigation interface.

Recommended columns:

  Column       Purpose
  ------------ -----------------------------------
  Timestamp    When anomaly occurred
  Station      Affected AWS
  Parameter    Temperature / Pressure / Humidity
  Status       Normal / Anomaly
  Score        ML anomaly evidence
  Root Cause   Fault taxonomy
  Severity     Low / Medium / High
  Confidence   Combined evidence strength

Example:

``` text
12:31:04 | AWS-01 | Temperature | Anomaly | Spike | High | 94%
12:44:12 | AWS-01 | Humidity    | Anomaly | Drift/Bias | Medium | 82%
```

Selecting a row should populate the detailed anomaly panel.

------------------------------------------------------------------------

# 16. Selected Anomaly Panel

This is the most important investigation area.

Recommended layout:

``` text
┌───────────────────────────────────────────────────────────────┐
│ SELECTED ANOMALY                                              │
│                                                               │
│ Temperature anomaly                                          │
│ Likely Sensor Fault                                           │
│                                                               │
│ Root Cause      Severity       Confidence                     │
│ Spike           HIGH           94%                            │
│                                                               │
│ Original Value: 55.2 °C                                      │
│ Expected Context: ~33 °C                                     │
│                                                               │
│ [ Evidence ] [ SHAP ] [ Spatial ] [ Recovery ]               │
└───────────────────────────────────────────────────────────────┘
```

This panel should consolidate evidence without forcing the user to
navigate away from the selected event.

------------------------------------------------------------------------

# 17. Evidence Panel

The evidence view should show why SkyGuard reached its interpretation.

Recommended structure:

``` text
EVIDENCE

Physics QC
✓ Range check
✕ Step-rate check

Isolation Forest
● Anomalous

Temporal behavior
● Sudden isolated jump

Neighboring stations
● 3 / 4 neighbors remain normal

Interpretation
→ Likely local sensor fault
```

This is preferable to showing only:

``` text
AI says: ANOMALY
```

------------------------------------------------------------------------

# 18. Weather Event vs Sensor Fault Visualization

This distinction is a core product feature.

The UI should make it visually obvious whether evidence points toward:

``` text
GENUINE WEATHER EVENT
```

or

``` text
LIKELY SENSOR / DATA FAULT
```

or

``` text
UNCERTAIN
```

Example:

``` text
┌─────────────────────────────────────────────┐
│ CONTEXTUAL INTERPRETATION                   │
│                                             │
│ ● LIKELY SENSOR FAULT                       │
│                                             │
│ Target station deviates strongly from       │
│ neighboring stations.                       │
│                                             │
│ Neighbor consensus: NORMAL                  │
└─────────────────────────────────────────────┘
```

Regional event:

``` text
┌─────────────────────────────────────────────┐
│ CONTEXTUAL INTERPRETATION                   │
│                                             │
│ ● POTENTIAL REGIONAL WEATHER EVENT          │
│                                             │
│ Multiple neighboring stations show          │
│ similar changes.                            │
│                                             │
│ Regional consensus: HIGH                    │
└─────────────────────────────────────────────┘
```

------------------------------------------------------------------------

# 19. Spatial Comparison Panel

When neighboring stations are available, display them directly.

Example:

``` text
                    TEMPERATURE

AWS-01  ● 55.0 °C   ← TARGET

AWS-02  ● 31.0 °C
AWS-03  ● 31.4 °C
AWS-04  ● 30.8 °C

Regional consensus: NORMAL
Target deviation: HIGH

Interpretation:
Likely local sensor anomaly
```

The spatial panel should answer:

> "Are other stations seeing the same thing?"

------------------------------------------------------------------------

# 20. SHAP Explanation Panel

The SHAP panel should provide feature-level attribution.

Example:

``` text
WHY WAS THIS FLAGGED?

Temperature       █████████  High contribution
Humidity          █████      Medium contribution
Pressure          ██         Low contribution
```

Below it:

``` text
Plain-English explanation:

The anomaly decision is driven primarily by
the observed temperature deviation, with
humidity providing additional supporting evidence.
```

The interface must not state that SHAP proves causation.

------------------------------------------------------------------------

# 21. Root-Cause Display

Use the standardized fault taxonomy everywhere.

``` text
SPIKE
FROZEN / STUCK
DRIFT / BIAS
COMMUNICATION / MISSING
```

Avoid alternative labels such as:

``` text
Random
Malfunction
Bad Sensor
```

unless they are explicitly mapped to the standardized taxonomy.

------------------------------------------------------------------------

# 22. Severity Design

Severity should be displayed prominently but separately from confidence.

Example:

``` text
SEVERITY
HIGH
```

and:

``` text
CONFIDENCE
94%
```

Do not combine them into one number.

The operator should understand that:

-   Severity = operational importance
-   Confidence = strength of evidence

------------------------------------------------------------------------

# 23. Sensor Health Panel

Sensor health should be longitudinal.

Recommended:

``` text
SENSOR HEALTH

87 / 100
HEALTHY

100 ┤───────────────╮
 80 ┤          ╭────╯
 60 ┤     ╭────╯
 40 ┤─────╯
    └──────────────────
       Time →
```

The panel should optionally show:

``` text
Recent anomalies: 3
Drift indicators: 1
Communication gaps: 0

Trend:
Stable
```

When degradation is detected:

``` text
72 / 100
DEGRADING

Recommendation:
Inspect / recalibrate sensor
```

The health score should not be presented as a predicted probability of
failure.

------------------------------------------------------------------------

# 24. Maintenance Panel

Maintenance recommendations should be concise and actionable.

Example:

``` text
MAINTENANCE RECOMMENDATION

Increasing drift detected over recent observations.

Recommended action:
Inspect / recalibrate sensor.

Reason:
Repeated deviation from expected temporal
and contextual behavior.
```

The interface should avoid claiming:

``` text
Sensor will fail in 3 days.
```

unless a validated predictive-maintenance model actually exists.

------------------------------------------------------------------------

# 25. Suggested Correction / Data Recovery Panel

When the advanced recovery module is enabled:

``` text
DATA RECOVERY

Original value
55.2 °C

Suggested value
33.7 °C

Basis
Temporal reconstruction + contextual evidence

Status
PENDING VALIDATION

[ Accept ] [ Reject ] [ Review ]
```

The UI must clearly communicate that the suggested value is not
automatically authoritative.

Original and suggested values must remain separate.

------------------------------------------------------------------------

# 26. Real-Time Replay Controls

The demo should include simple controls.

Recommended:

``` text
REPLAY

Dataset
[ Demo Scenario ▼ ]

Speed
[ 1x ▼ ]

[ ▶ Start ]
[ ⏸ Pause ]
[ ↻ Reset ]
```

Optional:

``` text
Current observation: 183 / 500
Processing latency: 18 ms
```

Latency must be measured from the actual implementation.

------------------------------------------------------------------------

# 27. Demo Scenario Selector

Predefined scenarios should make the prototype easy to demonstrate.

Recommended scenarios:

``` text
Healthy Baseline
Spike
Frozen Sensor
Gradual Drift
Communication Gap
Multivariate Inconsistency
Regional Weather Event
Isolated Station Fault
```

The selected scenario should be clearly visible.

------------------------------------------------------------------------

# 28. Empty States

The interface must handle unavailable evidence gracefully.

## No Spatial Data

``` text
SPATIAL EVIDENCE

Neighboring-station data unavailable.

Decision based on:
Physics + ML + temporal evidence
```

## No SHAP

``` text
EXPLANATION

Feature attribution is unavailable for this
processing mode.
```

## No Suggested Correction

``` text
DATA RECOVERY

No suggested correction is available for
this observation.
```

The UI should never imply that missing modules have produced results.

------------------------------------------------------------------------

# 29. Uncertain State

When evidence conflicts or is insufficient:

``` text
UNCERTAIN

The observation is unusual, but available
context is insufficient to confidently classify
it as a sensor fault or regional weather event.

Additional evidence recommended:
• Neighboring stations
• Longer temporal window
• Manual review
```

This state is important for preventing overconfident automation.

------------------------------------------------------------------------

# 30. Loading and Processing States

During replay:

``` text
PROCESSING OBSERVATION...
```

For ML:

``` text
Running anomaly detection...
```

For explanation:

``` text
Generating feature attribution...
```

Loading indicators should be short and should not block unrelated
dashboard information.

------------------------------------------------------------------------

# 31. Error States

Errors should be understandable to operators.

Bad:

``` text
ValueError: index out of bounds
```

Better:

``` text
DATA PROCESSING ERROR

The current observation could not be processed
because required sensor fields are missing.

Station: AWS-01
Timestamp: 12:34:10

Original record preserved.
```

Technical error details may be placed inside an expandable diagnostic
section.

------------------------------------------------------------------------

# 32. Interaction Model

The main interaction flow should be:

``` text
Dashboard opens
      ↓
Select station
      ↓
Observe current metrics
      ↓
Watch/replay time series
      ↓
Anomaly appears
      ↓
Select anomaly
      ↓
Review interpretation
      ↓
Inspect evidence
      ↓
Open SHAP explanation
      ↓
Check spatial context
      ↓
Review severity + health
      ↓
Review maintenance/recovery
```

The interface should not require users to understand ML terminology
before reaching the operational answer.

------------------------------------------------------------------------

# 33. Progressive Disclosure

Technical detail should appear progressively.

### Default View

Show:

-   Current state
-   Alert
-   Root cause
-   Severity
-   Confidence
-   Short explanation

### Expanded View

Show:

-   Physics rule results
-   Isolation Forest evidence
-   Temporal evidence
-   Spatial evidence
-   SHAP

### Advanced Diagnostics

Show:

-   Feature vector
-   Raw model scores
-   Threshold/configuration
-   Processing timing
-   Pipeline metadata

This keeps the main dashboard understandable.

------------------------------------------------------------------------

# 34. Accessibility

The design should not rely exclusively on color.

Every important state should include text:

``` text
HIGH
WARNING
HEALTHY
ANOMALY
UNCERTAIN
```

Charts should have:

-   Clear legends
-   Tooltips
-   Axis labels
-   Units
-   Distinguishable markers

Numerical values should include units:

``` text
31.4 °C
1008.2 hPa
61 %
```

------------------------------------------------------------------------

# 35. Responsive Behavior

The primary target is desktop/laptop use because the system is an
operational monitoring console.

Recommended responsive priorities:

### Wide Screen

``` text
Metrics
      ↓
Charts + Alerts
      ↓
Detailed Evidence
      ↓
Health + Maintenance
```

### Narrow Screen

Stack:

``` text
Metrics
↓
Alert
↓
Chart
↓
Anomaly
↓
Evidence
↓
Health
↓
Maintenance
```

Critical information must remain visible without horizontal scrolling.

------------------------------------------------------------------------

# 36. Component Architecture

Recommended reusable UI components:

``` text
components/
├── header.py
├── station_selector.py
├── metric_card.py
├── status_badge.py
├── trend_chart.py
├── anomaly_table.py
├── anomaly_detail.py
├── evidence_panel.py
├── shap_panel.py
├── spatial_panel.py
├── severity_badge.py
├── confidence_indicator.py
├── health_panel.py
├── maintenance_panel.py
├── recovery_panel.py
├── replay_controls.py
└── diagnostics_panel.py
```

The exact project structure may differ, but UI components should remain
modular.

------------------------------------------------------------------------

# 37. UI Data Contract

The dashboard should consume structured pipeline results rather than
reconstructing ML logic inside the UI.

Recommended object:

``` python
{
    "station_id": "...",
    "timestamp": "...",

    "observation": {
        "temperature": ...,
        "pressure": ...,
        "humidity": ...
    },

    "status": "...",

    "anomaly": {
        "is_anomaly": True,
        "score": ...,
        "parameter": "temperature"
    },

    "context": {
        "event_type": "...",
        "temporal_evidence": "...",
        "spatial_evidence": "..."
    },

    "diagnosis": {
        "root_cause": "Spike",
        "severity": "High",
        "confidence": ...
    },

    "explanation": {
        "shap_values": {},
        "plain_language": "..."
    },

    "health": {
        "score": ...,
        "status": "...",
        "trend": "..."
    },

    "maintenance": {
        "recommendation": "..."
    },

    "recovery": {
        "original_value": ...,
        "suggested_value": ...,
        "status": "..."
    }
}
```

The UI should not invent missing values.

------------------------------------------------------------------------

# 38. Visualization Design

## Time-Series

Use interactive Plotly charts.

Required:

-   Time on X-axis
-   Physical value on Y-axis
-   Units
-   Anomaly markers
-   Hover details
-   Selected-event highlighting

## Health Trend

Use a time-series or indicator showing health trajectory.

## Spatial Comparison

Use:

-   Station comparison table
-   Small multiple trend views
-   Geographic map only if actual station coordinates are available

Do not create a geographic visualization from invented coordinates.

------------------------------------------------------------------------

# 39. Anomaly Marker Design

Anomaly markers should communicate:

``` text
What?
When?
Where?
How severe?
```

Hover content:

``` text
Station: AWS-01
Time: 12:31:04
Parameter: Temperature
Value: 55.2 °C
Root Cause: Spike
Severity: High
Confidence: 94%
```

The exact values are runtime data, not design defaults.

------------------------------------------------------------------------

# 40. Dashboard Modes

The application may support:

## Mode 1 --- Monitoring

Focus:

-   Current station state
-   Trends
-   Active alerts
-   Health

## Mode 2 --- Investigation

Focus:

-   Selected anomaly
-   Evidence
-   SHAP
-   Spatial comparison
-   Root cause

## Mode 3 --- Replay / Demo

Focus:

-   Scenario
-   Streaming observations
-   Alerts
-   Processing latency

## Mode 4 --- Evaluation

Focus:

-   Ground truth
-   Predictions
-   Precision
-   Recall
-   F1
-   False positives
-   False negatives
-   Latency

Evaluation metrics should be clearly separated from live operational
indicators.

------------------------------------------------------------------------

# 41. Evaluation Screen

The evaluation page should show measurable results from controlled test
data.

Example structure:

``` text
MODEL / PIPELINE EVALUATION

Dataset: Injected anomaly benchmark

Precision       --
Recall          --
F1-score        --
False Positive  --
False Negative  --
Latency         --

Scenario Results
────────────────────────────────
Spike                 --
Frozen/Stuck          --
Drift/Bias            --
Communication/Missing --
Regional Event        --
Isolated Fault        --
```

No metric should be populated with fabricated numbers.

------------------------------------------------------------------------

# 42. Design for Trust

SkyGuard is making decisions about meteorological observations, so trust
is a core design requirement.

The UI should expose:

``` text
Evidence
Confidence
Original observation
Suggested value
Decision basis
```

It should avoid opaque language such as:

``` text
AI KNOWS THIS IS WRONG
```

Prefer:

``` text
Likely sensor fault

Evidence:
• Temperature step-rate violation
• Strong multivariate anomaly
• Neighboring stations remain normal
```

------------------------------------------------------------------------

# 43. Original Data Protection

The UI must visually distinguish:

``` text
ORIGINAL OBSERVATION
```

from:

``` text
SUGGESTED RECOVERY
```

Example:

``` text
Original: 55.2 °C
Suggested: 33.7 °C

⚠ Suggested value — validation required
```

Never display the suggested value in a way that makes it appear to have
replaced the original source value.

------------------------------------------------------------------------

# 44. Design Anti-Patterns

The SkyGuard UI should avoid:

### Generic AI Chatbot UI

The product is a monitoring/diagnostic console, not primarily a chatbot.

### Excessive AI Branding

Do not fill the dashboard with unnecessary "AI-powered" labels.

### Huge Model Claims

Do not display:

-   18B parameters
-   70B+ comparison
-   Agentic architecture

unless the actual architecture is changed and implemented.

### False Automation

Do not use:

-   "Self-Healed"
-   "Automatically fixed"
-   "Guaranteed correction"

for the normal MVP.

### Unsupported Precision

Do not display invented:

-   Accuracy
-   Precision
-   Recall
-   Latency
-   Correction quality

------------------------------------------------------------------------

# 45. Design Language for Product Copy

Use:

-   Detected
-   Flagged
-   Likely
-   Potential
-   Suggested
-   Evidence
-   Confidence
-   Observed
-   Reconstructed
-   Validation required

Avoid:

-   Guaranteed
-   Proven
-   Automatically fixed
-   Certain
-   Self-healed
-   Perfect
-   100% accurate

unless objectively supported by implementation/evaluation.

------------------------------------------------------------------------

# 46. Example Complete Anomaly Experience

## Step 1 --- Detection

``` text
HIGH PRIORITY

Temperature anomaly detected
```

## Step 2 --- Diagnosis

``` text
Likely Sensor Fault
Root Cause: Spike
Severity: High
Confidence: 94%
```

## Step 3 --- Evidence

``` text
Physics:
Step-rate violation

ML:
Strong anomaly

Temporal:
Sudden isolated jump

Spatial:
3 neighboring stations normal
```

## Step 4 --- Explanation

``` text
Temperature is the dominant feature
contributing to the anomaly decision.
```

## Step 5 --- Action

``` text
Maintenance recommendation:
Inspect / recalibrate sensor
```

## Step 6 --- Recovery

``` text
Suggested value:
33.7 °C

Original:
55.2 °C

Status:
Pending validation
```

This should be the ideal end-to-end UX.

------------------------------------------------------------------------

# 47. Example Regional Weather Event Experience

``` text
OBSERVATION

Temperature: 42.0 °C
Status: Unusual

ML:
Anomaly detected

Spatial:
4 neighboring stations show similar changes

Interpretation:
POTENTIAL REGIONAL WEATHER EVENT

Confidence:
Context supports regional behavior

Action:
Continue monitoring; do not classify
as an isolated sensor fault solely from
the extreme value.
```

This is one of the most important demonstrations of SkyGuard's value.

------------------------------------------------------------------------

# 48. Example Frozen Sensor Experience

``` text
ALERT

Sensor behavior anomaly

Root Cause:
FROZEN / STUCK

Evidence:
• Repeated identical values
• Expected temporal variation absent
• Persistence threshold exceeded

Severity:
MEDIUM

Sensor Health:
72 / 100 — DEGRADING

Recommendation:
Inspect sensing element / firmware path
```

------------------------------------------------------------------------

# 49. Example Communication Failure Experience

``` text
ALERT

Communication / Missing

Evidence:
• Expected observation not received
• Timestamp continuity gap
• Repeated telemetry gaps

Sensor Health:
Declining

Recommendation:
Inspect power/network/telemetry path
```

------------------------------------------------------------------------

# 50. Design Implementation Priorities

## Priority 1 --- Core MVP

Must implement:

-   Header
-   Station selector
-   Current metric cards
-   Time-series charts
-   Alert state
-   Anomaly table
-   Basic anomaly detail
-   Replay controls

## Priority 2 --- Intelligence

Add:

-   Evidence panel
-   Root-cause display
-   Severity
-   Confidence
-   SHAP panel
-   Spatial comparison
-   Sensor health
-   Maintenance recommendations

## Priority 3 --- Advanced

Add:

-   LSTM Autoencoder visualizations
-   Suggested recovery
-   Advanced temporal analysis
-   Evaluation workspace

## Priority 4 --- Future

Potential:

-   Live network monitoring
-   Geographic multi-station map
-   Remote station management
-   Production authentication
-   Cloud/edge integration

------------------------------------------------------------------------

# 51. Design Acceptance Criteria

The design is considered successful when:

-   [ ] A new user can identify the current station state quickly.
-   [ ] Current Temperature, Pressure and Humidity are immediately
    visible.
-   [ ] Active anomalies are visually prominent.
-   [ ] An anomaly can be selected for investigation.
-   [ ] Root cause, severity and confidence are clearly separated.
-   [ ] Physics, ML, temporal and spatial evidence can be inspected.
-   [ ] Genuine regional behavior can be visually distinguished from
    isolated faults.
-   [ ] SHAP explanations are understandable.
-   [ ] Sensor health is visible as a trend rather than only a single
    number.
-   [ ] Maintenance recommendations are actionable but not
    overconfident.
-   [ ] Suggested corrections are clearly separated from original
    observations.
-   [ ] Missing modules produce explicit unavailable states.
-   [ ] Real-time replay is easy to operate.
-   [ ] Evaluation metrics are separated from operational status.
-   [ ] The interface does not claim unsupported capabilities.
-   [ ] The dashboard remains readable on a laptop/desktop display.
-   [ ] The UI consumes structured pipeline outputs rather than
    duplicating model logic.

------------------------------------------------------------------------

# 52. Final Design Principle

The SkyGuard interface should make one idea immediately understandable:

> **SkyGuard does not simply flag unusual weather observations. It
> combines physical rules, multivariate ML, temporal behavior and
> neighboring-station evidence to determine whether an observation is
> more consistent with genuine weather or a sensor/data anomaly.**

The UI should therefore follow the same reasoning as the system:

``` text
SEE
 ↓
DETECT
 ↓
VERIFY
 ↓
EXPLAIN
 ↓
DIAGNOSE
 ↓
ACT
```

The product should feel like a **trusted meteorological quality-control
console** whose AI reasoning is visible, bounded and auditable.
