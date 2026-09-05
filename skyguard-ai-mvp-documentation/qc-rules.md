# SkyGuard AI — QC and Physics Rules

## Purpose

The deterministic QC layer is the transparent first analytical stage and supports a low-computation fast path.

Every rule should return:

```json
{
  "rule_id": "QC-TEMP-RANGE",
  "passed": false,
  "severity": "HIGH",
  "flag": "PHYSICAL_RANGE_VIOLATION",
  "message": "Temperature is outside configured range."
}
```

## Rules

### QC-01 Schema
Validate required fields, types, timestamp and station ID.

### QC-02 Missingness
Detect missing temperature, pressure, humidity and timestamp/communication gaps.

### QC-03 Physical range
Check each variable against a configured validated range.

### QC-04 Step/rate
```text
delta = current - previous
rate = delta / elapsed_time
```
Flag configured excessive changes.

### QC-05 Persistence
Detect repeated identical or near-identical observations over a configured window.

### QC-06 Dew point consistency
Use a Magnus-Tetens-style calculation:
```text
Td = dew_point(T, RH)
```
and check the basic relationship:
```text
Td ≤ T
```
within numerical tolerance.

### QC-07 Cross-variable consistency
Use temperature, pressure, humidity and derived variables as contextual evidence.

## Processing order

```text
Schema → Missingness → Range → Step/Rate → Persistence
→ Thermodynamic Consistency → Cross-Variable Consistency
```

Multiple rule violations must be retained.

## Fast path

```text
Observation
 ↓
QC
 ├─ Clearly invalid → immediate rule alert
 └─ Plausible → ML/context analysis
```

A rule violation is evidence, not automatic proof of sensor failure.

## Configuration

Thresholds belong in configuration, not scattered through code. Do not invent limits solely to improve demo performance.

## Testing

Every rule needs normal, boundary, invalid and relevant missing/edge-case tests.
