# SkyGuard AI — Machine Learning Specification

## Primary detector

**Isolation Forest** is the primary unsupervised multivariate anomaly detector.

```text
Temperature + Pressure + Humidity + Derived Features
                     ↓
               Feature Vector
                     ↓
              Isolation Forest
                     ↓
             Anomaly Evidence
```

## Baseline training

Train on representative normal observations from historical or clean simulated data. Injected anomalies must not contaminate the normal training baseline.

## Feature groups

Raw:
`temperature`, `pressure`, `humidity`

Potential temporal:
`temperature_delta`, `pressure_delta`, `humidity_delta`, rolling mean/std, slope, persistence count.

Potential derived:
`dew_point`, temperature-humidity relationship, pressure change.

Potential spatial:
neighbor median, deviation/MAD, target-minus-neighbor median, regional consensus.

Only implemented features may appear in the final model.

## Scaling

If scaling is used, fit only on baseline training data and persist the scaler.

## Configuration

Keep model parameters such as `n_estimators`, `max_samples`, `contamination`, and `random_state` configurable. Select them through validation.

## Output

```text
anomaly_score
is_anomaly
model_version
```

Anomaly score is model evidence, not probability of sensor failure.

## LSTM Autoencoder

Advanced/optional module.

```text
Sequence → LSTM Encoder → Latent State → Decoder
→ Reconstruction → Reconstruction Error
```

It may learn temporal/seasonal normal behavior. It is not part of the core MVP unless implemented, tested, evaluated and integrated.

## Evidence fusion

Keep these signals separate:

```text
Physics
ML
Temporal
Spatial
```

The decision layer combines available evidence explicitly.

## SHAP

Use SHAP for feature-level attribution where supported. It explains model output; it is not causal proof.

## Failure policy

If ML is unavailable, use available QC/context evidence and explicitly report ML unavailability. Never fabricate a model result.

## Retraining

Future retraining should account for new clean observations, seasonality, confirmed maintenance outcomes and model drift. Do not silently add unverified anomalies to the normal baseline.
