from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from .ensemble import MODEL_FEATURES
from ..config import DEFAULT_CONFIG
from ..features.engineering import create_features
from ..ingestion.csv_loader import canonicalize_observations, to_legacy_columns
from ..preprocessing.quality_control import run_quality_control
from ..utils.paths import resolve_project_path


@dataclass
class BaselineModel:
    scaler: StandardScaler
    model: IsolationForest
    model_version: str = "isolation-forest-baseline-v1"

    def predict(self, features: pd.DataFrame) -> pd.DataFrame:
        missing = [column for column in MODEL_FEATURES if column not in features.columns]
        if missing:
            raise ValueError(f"Missing model features: {missing}")
        values = self.scaler.transform(features[MODEL_FEATURES])
        scores = -self.model.decision_function(values)
        low, high = float(scores.min()), float(scores.max())
        normalized = (scores - low) / (high - low) if high > low else scores * 0
        result = features[["Location", "DateTime"]].copy()
        result["Baseline_Score"] = normalized
        result["Baseline_Anomaly"] = self.model.predict(values).astype(int) == -1
        result["Model_Version"] = self.model_version
        return result


def prepare_training_features(data: pd.DataFrame) -> pd.DataFrame:
    canonical = canonicalize_observations(data)
    checked = run_quality_control(canonical)
    return create_features(to_legacy_columns(checked))


def train_baseline(data: pd.DataFrame, model_dir: str | Path = DEFAULT_CONFIG.paths.model_dir) -> BaselineModel:
    features = prepare_training_features(data)
    clean = features
    if "ground_truth" in clean.columns:
        clean = clean[clean["ground_truth"].eq("NORMAL")]
    if clean.empty:
        raise ValueError("No clean observations are available for baseline training")
    scaler = StandardScaler().fit(clean[MODEL_FEATURES])
    model = IsolationForest(n_estimators=300, contamination=0.02, random_state=42, n_jobs=-1)
    model.fit(scaler.transform(clean[MODEL_FEATURES]))
    baseline = BaselineModel(scaler=scaler, model=model)
    output = resolve_project_path(model_dir)
    output.mkdir(parents=True, exist_ok=True)
    joblib.dump(baseline, output / "baseline_model.pkl")
    return baseline


def load_baseline(model_path: str | Path = DEFAULT_CONFIG.paths.model_dir / "baseline_model.pkl") -> BaselineModel:
    baseline = joblib.load(resolve_project_path(model_path))
    if not isinstance(baseline, BaselineModel):
        raise TypeError("Stored model is not a SkyGuard BaselineModel")
    return baseline


def score_with_baseline(data: pd.DataFrame, baseline: BaselineModel | None = None) -> pd.DataFrame:
    features = prepare_training_features(data)
    baseline = baseline or load_baseline()
    return baseline.predict(features)
