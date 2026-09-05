# SkyGuard AI Implementation Roadmap

This roadmap tracks the documented local MVP requirements against the current implementation. Production infrastructure explicitly marked future in the PRD is excluded from the MVP completion target.

## Current Baseline

- Overall local MVP estimate: approximately 65%.
- Validation baseline: 12 automated tests, successful batch pipeline, dashboard smoke test.
- Current implementation is a local batch prototype, not a production service.

## Priority 0: Core MVP Completion

1. **Structured quality control**
   - Return machine-readable QC results for schema, missingness, timestamp gaps, range, rate, persistence, thermodynamic consistency, duplicates, and cross-variable checks.
   - Preserve multiple violations per observation.
2. **Canonical pipeline contract**
   - Expose structured observation, quality, anomaly, context, diagnosis, explanation, health, maintenance, and recovery fields.
   - Keep original observations immutable.
3. **Clean-baseline detection**
   - Separate baseline training from inference in the main pipeline.
   - Report model version and explicit unavailable states.
4. **Evaluation completeness**
   - Add per-root-cause metrics, event-versus-fault metrics, false-positive/negative rates, confusion matrices, and measured latency.
5. **Dashboard acceptance**
   - Add QC evidence, spatial evidence, recovery state, baseline/model status, and replay controls to the operator workflow.

## Priority 1: Intelligence Quality

1. Add station metadata and real neighbor selection using coordinates when available.
2. Improve temporal persistence, drift, and trend evidence with configurable windows.
3. Integrate optional SHAP attribution into anomaly details when installed.
4. Replace cumulative health with rolling health, trend, and recovery behavior.
5. Add regional-event, isolated-fault, seasonal-extreme, and repeated-fault evaluation scenarios.

## Priority 2: Advanced Modules

1. Implement and test an actual LSTM autoencoder only when TensorFlow is explicitly installed.
2. Generate sequence reconstruction errors and integrate them as a separate temporal evidence signal.
3. Add model-based recovery only after raw-value immutability and evaluation are established.

## Priority 3: Production Scope

- MQTT/Kafka/WIS2 ingestion
- Cloud deployment and production database
- Authentication and authorization
- REST API
- ESP32/edge deployment
- Predictive failure-date modeling

## Definition of Done

A roadmap item is complete when its code, focused tests, documented interface, and executable validation evidence are present. Advanced and production capabilities must remain visibly unavailable until those conditions are met.
