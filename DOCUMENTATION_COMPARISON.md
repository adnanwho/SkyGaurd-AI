# SkyGuard AI Documentation Comparison

## 1. Executive Summary

Overall winner: HYBRID.

The existing version under `skyguard-ai-mvp-documentation/` is the stronger product and architecture source. It contains the detailed PRD, architecture, UX specification, data schema, QC specification, ML specification, evaluation plan, API/interface notes, technical stack, and documentation index. It is comprehensive and should remain the primary source for what SkyGuard AI is supposed to become.

The new version under `skyguard-ai-additional-docs/` is not a replacement. It is a useful operating layer: clearer user flow, tighter design brief, stronger testing discipline, and a better layer-by-layer engineering sequence. It should be merged into the final documentation hierarchy as concise companion documents, not allowed to duplicate or override the deeper baseline specs.

The actual implementation is still early. Layer 1 has been completed: canonical schemas/config plus 12 passing tests. All later modules remain placeholders. Therefore, any final documentation must clearly distinguish implemented behavior from planned behavior.

Direct answer: if continuing today, Codex should follow the existing documentation as the product/specification baseline, merge the new engineering plan, testing strategy, user flow, and design brief as implementation guidance, and use this implementation order: Audit -> Foundation -> Data Ingestion -> Anomaly Injection -> Preprocessing -> QC -> Features -> Isolation Forest -> Temporal Verification -> Spatial Verification -> Event/Fault Classification -> Explainability -> Severity/Confidence -> Sensor Health -> Maintenance -> Recovery -> Pipeline -> Dashboard -> Evaluation -> Hardening.

## 2. Existing Version Analysis

Existing version location:

- `skyguard-ai-mvp-documentation/`

Key files:

- `prd.md`
- `architecture.md`
- `design.md`
- `implementation-plan.md`
- `data-schema.md`
- `qc-rules.md`
- `ml-spec.md`
- `evaluation.md`
- `tech-stack.md`
- `api-spec.md`
- `README.md`
- `DOCUMENTATION_INDEX.md`

Strengths:

- Best product definition and problem framing.
- Strong canonical workflow: `Validate -> Detect -> Verify -> Explain -> Diagnose -> Recover`.
- Clearly separates MVP, advanced, and future capabilities.
- Explicitly warns against fabricated metrics, unsupported claims, autonomous self-healing language, and SHAP-as-causality.
- Provides the most complete architecture and dashboard specification.
- Defines core variables, fault taxonomy, data integrity rules, evaluation protocol, and module boundaries.

Weaknesses:

- Some files are long enough that they are less convenient as day-to-day coding instructions.
- `implementation-plan.md` groups multiple responsibilities into broad phases, which can tempt oversized implementation batches.
- Existing docs mention advanced functionality such as LSTM Autoencoder and suggested recovery in many places; they usually label this correctly, but readers must stay disciplined about MVP boundaries.
- Root project `README.md` is empty, so the usable documentation lives in a nested folder rather than the repository entry point.

Verdict:

- KEEP as the main product and technical specification.
- MERGE with the new docs for workflow, user-flow summary, and testing discipline.

## 3. New Version Analysis

New version location:

- `skyguard-ai-additional-docs/`

Key files:

- `user-flow.md`
- `design-brief.md`
- `testing-strategy.md`
- `tdd.md`
- `engineering-plan.md`

Strengths:

- More concise and implementation-friendly.
- `engineering-plan.md` gives the best dependency order for Codex-style incremental work.
- `testing-strategy.md` is sharper than the existing test descriptions for layer-by-layer validation.
- `user-flow.md` provides a clear operator journey: station -> anomaly -> evidence -> diagnosis -> action.
- `design-brief.md` is a compact dashboard summary that is easier to use during implementation than the full `design.md`.
- `tdd.md` is a useful bridge between architecture and implementation.

Weaknesses:

- Not as complete as the existing docs.
- Mostly summarizes rather than expands the product requirements.
- Does not replace `prd.md`, `architecture.md`, `ml-spec.md`, `qc-rules.md`, or `evaluation.md`.
- Could become duplicative if not indexed carefully.

Verdict:

- USE for developer workflow, testing, and concise UX guidance.
- MERGE into the documentation hierarchy, but do not treat as the sole source of truth.

## 4. Repository/Code Audit

Current implementation evidence:

- `src/schemas.py` implements Layer 1 canonical contracts:
  - `RawObservation`
  - `ProcessedObservation`
  - `QCResult`
  - `QualityResult`
  - `AnomalyResult`
  - `ContextResult`
  - `DiagnosticResult`
  - `ExplanationResult`
  - `HealthResult`
  - `MaintenanceRecommendation`
  - `RecoverySuggestion`
  - `StationMetadata`
  - `SchemaError`
  - canonical enums
  - `validate_observation`
  - `validate_observation_dataframe`
- `src/config.py` implements Layer 1 configuration contracts:
  - `VariableThreshold`
  - `QCConfig`
  - `IsolationForestConfig`
  - `FeatureFlagConfig`
  - `PathConfig`
  - `AppConfig`
  - `DEFAULT_CONFIG`
- `requirements.txt` now lists required and planned dependencies.
- `tests/test_schemas.py` and `tests/test_config.py` contain real tests.
- Full test run result: `12 passed`.

Placeholders / missing implementation:

- `src/data_simulator.py`
- `src/anomaly_injector.py`
- `src/preprocessing.py`
- `src/rule_checks.py`
- `src/feature_engineering.py`
- `src/isolation_forest_model.py`
- `src/spatial_consistency.py`
- `src/event_classifier.py`
- `src/explainability.py`
- `src/scoring.py`
- `src/sensor_health.py`
- `src/maintenance.py`
- `src/pipeline.py`
- `dashboard/app.py`
- `run.py`
- most existing test files
- sample datasets and models

Working well:

- Layer 1 now matches the documented MVP field names.
- Raw observation immutability is reflected in `ProcessedObservation.from_raw()` and `RecoverySuggestion.original_values`.
- The canonical taxonomy is now encoded in tests.

Still broken or documentation-only:

- No ingestion, simulator, QC engine, ML, dashboard, replay, or evaluation is implemented.
- Root `README.md` remains empty because runnable application commands are not true yet.
- No model performance metrics exist.

## 5. Requirements Comparison

| Area | Existing Version | New Version | Better Source | Reason |
|---|---|---|---|---|
| Problem definition | Deep PRD with users, goals, risks, non-goals | Concise restatement | Existing | Existing gives the fuller SIH-aligned product context |
| Target users | Meteorologists, AWS maintenance, forecasting systems, researchers, operators | Operator-focused | Merge | Existing covers all stakeholders; new sharpens operator workflow |
| Functional requirements | Full FR list and acceptance criteria | Summary through workflow and TDD | Existing | More complete and traceable |
| MVP scope | Good P0/P1/P2/P3 boundaries | Cleaner concise priority list | Merge | Existing has detail; new has better build discipline |
| Non-goals | Strong future-scope boundaries | Brief future list | Existing | More explicit about what not to claim |
| Acceptance criteria | Detailed product and design acceptance | Layer DoD and technical acceptance | Merge | Both are useful at different levels |

## 6. Architecture Comparison

Both versions agree on the core architecture:

```text
AWS Observation
-> Schema Validation
-> Preprocessing
-> Physics / Rule QC
-> Feature Engineering
-> Isolation Forest
-> Temporal Verification
-> Spatial Verification
-> Weather Event vs Sensor Fault
-> SHAP Explanation
-> Root Cause
-> Severity + Confidence
-> Sensor Health
-> Maintenance Recommendation
-> Suggested Correction / Data Recovery
-> Dashboard
```

Existing architecture strengths:

- More complete layer descriptions.
- Stronger error handling and traceability sections.
- Better module responsibility table.
- Clearer security, storage, scalability, and deployment boundaries.

New architecture strengths:

- Better concise TDD shape.
- Explicitly tells implementers to reuse equivalent modules instead of duplicating.
- Clearer treatment of unavailable states.

Winner: MERGE, with existing `architecture.md` as canonical and new `tdd.md` as the developer-facing summary.

Easiest architecture to implement correctly:

- Existing architecture for correctness.
- New engineering plan for order.

## 7. Data Model Comparison

Existing version:

- `data-schema.md` correctly defines the MVP raw observation:
  - `station_id`
  - `timestamp`
  - `temperature`
  - `pressure`
  - `humidity`
  - optional `latitude`, `longitude`, `elevation`
- Defines processed record sections and enums.
- Strong immutability rule.

New version:

- Reinforces raw immutability and recovery separation.
- Does not define schema with as much precision.

Actual code:

- Now aligns with existing `data-schema.md` after Layer 1.

Winner: EXISTING for data schema, with NEW reinforcing user-flow and recovery review expectations.

## 8. ML Comparison

Existing version:

- `ml-spec.md` clearly names Isolation Forest as the primary MVP detector.
- Defines raw, temporal, derived, and spatial feature groups.
- Warns against training leakage.
- Separates scaling, persistence, anomaly score interpretation, SHAP, and LSTM Autoencoder scope.

New version:

- Confirms Isolation Forest, training/inference separation, persistence, leakage prevention, and LSTM as advanced.
- Provides better engineering order around ML.

Winner: EXISTING for ML specification; NEW for sequencing.

Important conclusion:

- LSTM Autoencoder remains P2 advanced/optional.
- No model accuracy, precision, recall, F1, or confidence quality may be claimed until the evaluation layer exists.

## 9. QC Comparison

Both versions cover required QC:

- physical range
- rate/step
- persistence/frozen
- missingness/communication
- thermodynamic consistency
- dew-point consistency
- cross-variable consistency

Existing version:

- `qc-rules.md` gives the clearer QC result example and processing order.
- Explicitly states rule violations are evidence, not automatic proof of sensor failure.

New version:

- Strongly reinforces independent tests for each QC rule.

Winner: MERGE.

Implementation note:

- QC is not implemented yet. Layer 5 should use `QCResult` from `src/schemas.py` and thresholds from `src/config.py`.

## 10. User Flow Comparison

Existing version:

- `design.md` contains extensive user questions, layout ideas, dashboard modes, evidence panels, recovery UX, and design anti-patterns.

New version:

- `user-flow.md` is the best concise operator workflow:
  - open dashboard
  - select station
  - view T/P/RH
  - review alert
  - inspect QC/ML/temporal/spatial evidence
  - decide weather event vs sensor fault
  - review diagnosis, severity, confidence, health, recommendation, recovery

Winner: NEW for flow summary; EXISTING for full UX detail.

Actual dashboard:

- `dashboard/app.py` is empty. All dashboard behavior is documentation-only.

## 11. Design Comparison

Existing `design.md`:

- Best full design source.
- Strong information hierarchy.
- Covers empty states, uncertainty states, SHAP language, recovery safety, replay controls, evaluation screen, accessibility, and anti-patterns.

New `design-brief.md`:

- Best short implementation brief.
- Easier to keep open while coding dashboard components.

Winner: MERGE.

Recommended use:

- Use `design.md` as canonical UX specification.
- Use `design-brief.md` as the quick dashboard implementation checklist.

## 12. Testing Comparison

Existing version:

- `evaluation.md`, `architecture.md`, and `implementation-plan.md` describe test categories and evaluation protocol.
- Good coverage targets, but spread across multiple docs.

New version:

- `testing-strategy.md` is clearer and more practical for TDD.
- Directly maps tests to layers and unavailable/uncertain cases.

Actual tests:

- 12 Layer 1 tests pass.
- Later-layer tests are placeholders.

Winner: NEW for test strategy, merged with existing `evaluation.md` for metrics protocol.

## 13. Engineering Plan Comparison

Existing `implementation-plan.md` order:

```text
Setup -> Data -> Detection Core -> Contextual Intelligence
-> XAI + Health -> Dashboard + Replay -> Evaluation + QA
-> Advanced Modules -> Packaging
```

New `engineering-plan.md` order:

```text
Audit -> Configuration/Data Contracts -> Ingestion -> Anomaly Injection
-> Preprocessing -> QC -> Features -> Isolation Forest -> Temporal
-> Spatial -> Event/Fault Classification -> Explainability
-> Severity/Confidence -> Sensor Health -> Maintenance -> Recovery
-> Pipeline -> Dashboard -> Evaluation -> Hardening
```

Winner: NEW.

Reason:

- The new plan better matches dependency order and prevents jumping into dashboard or ML before data contracts, ingestion, injection, preprocessing, and QC are testable.
- It also fits the current codebase state, where only Layer 1 is real.

## 14. MVP Scope Comparison

Recommended final scope:

| Priority | Features |
|---|---|
| P0 - Required MVP | Data ingestion/simulation, anomaly injection, preprocessing, deterministic QC, feature engineering, Isolation Forest, basic diagnosis, pipeline, dashboard, replay, evaluation, tests |
| P1 - Important Intelligence | Temporal verification, spatial verification, weather event vs sensor fault, SHAP, severity/confidence, sensor health, maintenance recommendation |
| P2 - Advanced | LSTM Autoencoder, advanced seasonal modeling, richer/model-based recovery |
| P3 - Future/Production | MQTT/Kafka, WIS2.0, cloud, production DB, auth, edge/ESP32, production API infrastructure |

Existing version:

- More detailed and mostly correct about MVP/advanced/future.

New version:

- Cleaner priority and engineering order.

Incorrect MVP treatment:

- Neither set fatally treats LSTM or production infrastructure as MVP, but the existing docs mention advanced features often. Final docs should add visible labels wherever advanced features are referenced.

Winner: MERGE.

## 15. Terminology Audit

Canonical terms to keep:

- `Spike`
- `Frozen/Stuck`
- `Drift/Bias`
- `Communication/Missing`
- `Suggested Correction / Data Recovery`
- `Weather Event`
- `Sensor Fault`
- `Severity`
- `Confidence`
- `Sensor Health`
- `SHAP feature attribution`

Terms to avoid as structured states:

- sensor broken
- bad reading
- abnormal sensor
- self-healing
- proven cause
- guaranteed correction
- predictive maintenance, unless a validated predictive model exists

Existing version:

- Strong terminology rules in `prd.md`, `design.md`, and `architecture.md`.

New version:

- Consistent with the canonical taxonomy and reinforces recovery wording.

Actual code:

- Layer 1 now encodes the canonical taxonomy.

Winner: TIE/MERGE.

## 16. Code Compatibility Analysis

| Requirement | Existing Code | New Spec | Compatibility | Required Action |
|---|---|---|---|---|
| Canonical raw observation | Implemented in Layer 1 | Required | Compatible | Preserve and build ingestion against `RawObservation` |
| Processed output contract | Implemented in Layer 1 | Required | Compatible | Preserve and populate in later pipeline |
| Config thresholds | Implemented in Layer 1 | Required | Compatible | Use in QC; avoid hardcoding |
| CSV/historical adapter | Missing | Required | Needs new module/function | Implement Layer 2 |
| Simulator | Missing | Required if no historical data | Needs new module | Implement Layer 2 |
| Replay input | Missing | Required | Needs new function | Implement after ingestion, before dashboard |
| Anomaly injection | Missing | Required | Needs new module | Implement Layer 3 |
| Preprocessing | Missing | Required | Needs implementation | Implement Layer 4 |
| QC rules | Missing | Required | Needs implementation | Implement Layer 5 using `QCResult` |
| Feature engineering | Missing | Required | Needs implementation | Implement Layer 6 |
| Isolation Forest | Missing | Required | Needs implementation | Implement Layer 7 |
| Temporal verification | Missing | Required for intelligence | Needs implementation | Implement simple MVP temporal checks |
| Spatial verification | Missing | Required for core value proposition | Needs implementation | Implement neighbor evidence, no invented coordinates |
| Event/fault classification | Missing | Required | Needs implementation | Implement evidence fusion |
| SHAP | Missing | Important | Needs optional integration | Return unavailable state when unsupported |
| Severity/confidence | Missing | Required | Needs implementation | Make diagnostic confidence separate from model score |
| Sensor health | Missing | Important | Needs implementation | Use transparent operational score |
| Maintenance | Missing | Important | Needs implementation | Evidence-driven recommendations |
| Recovery | Missing | Optional/advanced-ish | Needs implementation after diagnosis | Preserve raw values; suggested values separate |
| Pipeline | Missing | Required | Needs implementation | Integrate after backend layers exist |
| Dashboard | Missing | Required | Needs implementation | Consume pipeline output only |
| Evaluation | Missing | Required | Needs implementation | Calculate actual metrics from ground truth |

Implementing new docs would not break existing functionality because little runtime behavior exists, but it must preserve the Layer 1 contracts and tests.

## 17. Scorecard

Scores reflect documentation usefulness for this project, not implementation status.

| Category | Existing | New | Winner | Reason |
|---|---:|---:|---|---|
| Clarity | 8 | 9 | New | New docs are shorter and more direct |
| Completeness | 10 | 7 | Existing | Existing covers full PRD, architecture, ML, QC, evaluation, design |
| Technical correctness | 9 | 8 | Existing | Existing gives more precise technical constraints |
| Consistency | 8 | 9 | New | New docs are compact and less repetitive |
| Implementation usefulness | 8 | 9 | New | Engineering order and testing are more actionable |
| Testability | 8 | 9 | New | Testing strategy maps cleanly to layers |
| MVP suitability | 8 | 9 | New | New plan better prevents premature advanced work |
| Maintainability | 8 | 8 | Tie | Existing is thorough; new is easier to maintain |
| Scalability | 9 | 7 | Existing | Existing covers station-independent architecture and future deployment better |
| Explainability | 9 | 8 | Existing | Existing has deeper SHAP and operator explanation guidance |
| Developer usability | 8 | 9 | New | New docs are better day-to-day implementation guides |
| Codex/AI-agent usability | 7 | 10 | New | New engineering plan is explicitly layer-by-layer and stop-gated |

## 18. Keep / Replace / Merge / Remove / Defer Matrix

| Area | Decision | Reason |
|---|---|---|
| `prd.md` | KEEP EXISTING | Best full product requirements source |
| `architecture.md` | KEEP EXISTING | Most complete architecture and boundaries |
| `design.md` | KEEP EXISTING | Best detailed UX specification |
| `implementation-plan.md` | MERGE | Keep as phase overview, but defer to new engineering order |
| `data-schema.md` | KEEP EXISTING | Canonical schema source |
| `qc-rules.md` | KEEP EXISTING | Strong QC rule contract |
| `ml-spec.md` | KEEP EXISTING | Strong ML boundaries and leakage rules |
| `evaluation.md` | KEEP EXISTING | Best metric protocol |
| `tech-stack.md` | KEEP EXISTING | Sufficient stack definition |
| `api-spec.md` | KEEP EXISTING | Useful internal interface/future API distinction |
| `DOCUMENTATION_INDEX.md` | MODIFY LATER | Needs to include additional docs |
| `user-flow.md` | USE NEW | Best concise operator journey |
| `design-brief.md` | USE NEW | Best dashboard implementation checklist |
| `testing-strategy.md` | USE NEW | Best layer test strategy |
| `tdd.md` | USE NEW/MERGE | Good technical summary, but should reference canonical architecture |
| `engineering-plan.md` | USE NEW | Best implementation order |
| Self-healing terminology | REMOVE | Conflicts with MVP recovery language |
| LSTM in MVP | DEFER | Advanced unless implemented and validated |
| Production API/cloud/auth/edge | DEFER | P3 future scope |

## 19. Recommended Final Documentation Structure

Recommended final hierarchy:

```text
README.md
skyguard-ai-mvp-documentation/
  DOCUMENTATION_INDEX.md
  prd.md
  architecture.md
  tdd.md
  data-schema.md
  qc-rules.md
  ml-spec.md
  design.md
  design-brief.md
  user-flow.md
  engineering-plan.md
  implementation-plan.md
  testing-strategy.md
  evaluation.md
  tech-stack.md
  api-spec.md
```

Recommended merge actions, later:

- Move or copy the additional docs into the main documentation folder.
- Update `DOCUMENTATION_INDEX.md` to include them.
- Keep `implementation-plan.md` as high-level phase planning.
- Use `engineering-plan.md` as the authoritative coding order.
- Keep `design.md` as full UX spec and `design-brief.md` as dashboard quick reference.
- Keep `evaluation.md` and `testing-strategy.md` separate because evaluation metrics and test coverage serve different purposes.

Do not create more documents unless a real gap appears.

## 20. Recommended Final Architecture

Final reconciled architecture:

```text
Raw AWS Observation
  -> Schema Validation
  -> Data Ingestion / Replay Ordering
  -> Preprocessing
  -> Physics and Rule-Based QC
  -> Feature Engineering
  -> Isolation Forest
  -> Temporal Verification
  -> Spatial Verification
  -> Evidence Fusion
  -> Weather Event vs Sensor Fault
  -> SHAP Feature Attribution, when available
  -> Root Cause Classification
  -> Severity + Diagnostic Confidence
  -> Sensor Health
  -> Maintenance Recommendation
  -> Suggested Correction / Data Recovery, when enabled
  -> Pipeline Output
  -> Streamlit / Plotly Dashboard
  -> Evaluation Reports
```

Core architectural rules:

- Raw observations are immutable.
- Recovery suggestions are separate records.
- QC is evidence, not proof.
- Isolation Forest is the primary MVP multivariate detector.
- Temporal and spatial verification must be explicit evidence.
- SHAP is attribution, not causality.
- Confidence is diagnostic evidence strength, not model accuracy.
- Dashboard consumes pipeline output and does not duplicate backend logic.
- Evaluation metrics come only from reproducible runs.

## 21. Implementation Impact

Files to preserve:

- `src/schemas.py`
- `src/config.py`
- `tests/test_schemas.py`
- `tests/test_config.py`
- `IMPLEMENTATION_ANALYSIS.md`
- `IMPLEMENTATION_STATUS.md`
- all source placeholder filenames, because they match intended module boundaries

Files to modify later:

- `src/data_simulator.py`
- `src/anomaly_injector.py`
- `src/preprocessing.py`
- `src/rule_checks.py`
- `src/feature_engineering.py`
- `src/isolation_forest_model.py`
- `src/spatial_consistency.py`
- `src/event_classifier.py`
- `src/explainability.py`
- `src/scoring.py`
- `src/sensor_health.py`
- `src/maintenance.py`
- `src/pipeline.py`
- `dashboard/app.py`
- `run.py`
- `README.md`
- `DOCUMENTATION_INDEX.md`

Files to create later:

- `src/historical_adapter.py`, if ingestion needs a separate adapter instead of a simple loader function.
- Evaluation runner/module when Layer 18 starts.
- Dashboard component modules only if `dashboard/app.py` becomes too large.
- Real sample data after simulator/ingestion exist.

Files to deprecate:

- None yet. The current placeholder modules are useful named targets.

Modules to refactor:

- None beyond preserving Layer 1 contracts. Later modules are empty.

Tests to add:

- Data ingestion tests.
- Anomaly injection tests.
- Preprocessing tests.
- QC tests.
- Feature tests.
- Isolation Forest tests.
- Temporal/spatial tests.
- Classification/scoring tests.
- Explainability fallback tests.
- Health/maintenance/recovery tests.
- Pipeline integration tests.
- Dashboard smoke tests.
- Evaluation tests.

Dashboard changes:

- Build only after backend pipeline can produce structured results.
- Use `design.md`, `design-brief.md`, and `user-flow.md`.

ML changes:

- Implement training/inference separation and persistence after features exist.
- No accuracy claims before evaluation.

Data changes:

- Implement ingestion and simulator against `RawObservation`.
- Preserve clean data and injected data separately.

## 22. Risks

- If both documentation sets remain in separate folders without index guidance, future implementation may follow inconsistent instructions.
- Existing docs are comprehensive but long; developers may skip important constraints.
- New docs are concise but incomplete; using only them would lose important product and evaluation detail.
- Dashboard work before pipeline work would cause duplicated business logic.
- ML work before data/preprocessing/QC would produce fragile demos.
- Recovery could be over-marketed as self-healing.
- LSTM could distract from the MVP.
- Confidence could be fabricated if not derived from explicit evidence.
- Evaluation metrics could become presentation numbers without reproducible runs.

## 23. Final Verdict

Overall winner: HYBRID.

Why:

- Existing version is the better source for product truth, architecture depth, data/QC/ML/evaluation details, and design completeness.
- New version is the better source for implementation workflow, test discipline, and compact operator UX.
- The current codebase needs disciplined layer-by-layer implementation more than it needs another broad rewrite of requirements.

Best parts of existing version:

- `prd.md` product framing and acceptance criteria.
- `architecture.md` module boundaries and canonical flow.
- `data-schema.md` canonical field definitions.
- `qc-rules.md` deterministic QC contract.
- `ml-spec.md` Isolation Forest and leakage rules.
- `evaluation.md` reproducible metrics protocol.
- `design.md` detailed operator dashboard guidance.

Best parts of new version:

- `engineering-plan.md` dependency-ordered implementation plan.
- `testing-strategy.md` layer-by-layer verification.
- `user-flow.md` concise operator flow.
- `design-brief.md` concise dashboard build checklist.
- `tdd.md` implementation-facing architecture summary.

Things to remove:

- Any structured use of "self-healing" for MVP.
- Any claim that dashboard, ML, QC, or evaluation is implemented before code/tests prove it.
- Any unsupported model-size, agentic, predictive-maintenance, or performance-metric claims.

Things to merge:

- New docs into the main documentation index.
- Existing implementation plan with new engineering plan.
- Existing design spec with new design brief/user flow.
- Existing evaluation spec with new testing strategy.

Things to rewrite:

- Root `README.md`, after real runnable layers exist.
- `DOCUMENTATION_INDEX.md`, to include the new docs and final source-of-truth hierarchy.
- `implementation-plan.md`, later, if it conflicts with `engineering-plan.md`.

Things to defer:

- LSTM Autoencoder.
- Advanced recovery.
- Production API/cloud/auth/edge/WIS2.0.
- Any predictive maintenance model.

## 24. Recommended Next Step

Use this final source-of-truth hierarchy:

1. Actual validated implementation and passing tests.
2. `prd.md`.
3. `architecture.md` plus `tdd.md`.
4. `data-schema.md`.
5. `qc-rules.md` and `ml-spec.md`.
6. `user-flow.md`, `design.md`, and `design-brief.md`.
7. `engineering-plan.md`.
8. `testing-strategy.md` and `evaluation.md`.
9. `tech-stack.md` and `api-spec.md`.
10. Future roadmap sections only after MVP is stable.

Continue implementation with:

```text
Layer 2 - Data Ingestion
```

Layer 2 should implement only:

- CSV/local dataframe ingestion.
- Historical adapter if needed.
- Basic observation sequence production.
- Timestamp parsing/ordering.
- Station ID preservation.
- Missing value representation.
- Replay input iterator without ML or QC.
- Tests proving ingestion works against `RawObservation`.

Do not implement anomaly injection, preprocessing, QC, ML, dashboard, or evaluation until Layer 2 passes and `IMPLEMENTATION_STATUS.md` is updated.
