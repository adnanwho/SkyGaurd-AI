# SkyGuard AI

SkyGuard AI is a local Python MVP for quality control and anomaly detection in Automatic Weather Station observations. It combines deterministic QC, feature-based ensemble detection, temporal/spatial context, fault diagnosis, sensor health, maintenance recommendations, and evaluation.

## Current status

Implemented:

- Canonical and legacy CSV ingestion
- Deterministic multi-station simulation and labeled anomaly injection
- Range, rate, missingness, duplicate, persistence, and thermodynamic QC
- Leakage-safe temporal feature engineering
- Isolation Forest, ECOD, COPOD, and HBOS ensemble detection
- Spatial/temporal context and event-versus-fault diagnosis
- Severity, confidence, explanations, health, maintenance, and recovery suggestions
- Batch pipeline, evaluation metrics, CLI, Streamlit dashboard, and tests

Future work:

- LSTM autoencoder training and scoring when TensorFlow is installed
- Live ingestion and production deployment

SHAP feature attribution is active when installed and is included in the pipeline output. It reports feature contribution, not causal proof.

Additional commands:

```bash
python main.py --train-baseline
python main.py --score-baseline
python main.py --evaluate
python main.py --lstm-status
python main.py --train-lstm
```

## Project structure

Runtime code lives under `src/skyguard` and is organized by ingestion, preprocessing, features, detection, context, diagnosis, explainability, health, evaluation, and replay. The Streamlit entry point is `dashboard/app.py`. Generated model and export artifacts live under `models/trained`, `outputs/exports`, and `outputs/evaluation`.

## Setup

```bash
python -m pip install -r requirements.txt
```

## Run

```bash
python main.py --input data/processed/SkyGuard_clean_3hourly.csv
```

The command writes `outputs/exports/anomaly_detection_results.csv`. To run a deterministic demo dataset:

```bash
python main.py --simulate --output outputs/exports/simulated_results.csv
```

To launch the dashboard:

```bash
streamlit run dashboard/app.py
```

## Test

```bash
python -m pytest -q
```

For development guidance, see [docs/development.md](docs/development.md) and [docs/architecture.md](docs/architecture.md).
