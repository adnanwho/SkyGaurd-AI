from __future__ import annotations

from pathlib import Path
from dataclasses import asdict
from typing import Any

import pandas as pd

from .detection.ensemble import run_anomaly_pipeline
from .diagnosis.diagnostics import add_context_and_diagnosis
from .features.engineering import create_features
from .ingestion.csv_loader import canonicalize_observations, to_legacy_columns
from .health.operations import add_operational_intelligence
from .preprocessing.quality_control import run_quality_control
from .ingestion.schema import validate_observation
from .utils.paths import resolve_project_path
from .utils.logging import get_logger


LOGGER = get_logger("skyguard.pipeline")


def run_pipeline(data: pd.DataFrame, contamination: float = 0.02) -> pd.DataFrame:
    """Run the complete local MVP pipeline and return traceable row-level results."""
    LOGGER.info("Input received")
    canonical = canonicalize_observations(data)
    LOGGER.info("Schema normalization completed")
    checked = run_quality_control(canonical)
    LOGGER.info("Quality control completed")
    legacy = to_legacy_columns(checked)
    featured = create_features(legacy)
    LOGGER.info("Features generated")
    detected = run_anomaly_pipeline(featured, contamination=contamination)
    LOGGER.info("Models and ensemble scoring completed")
    result = detected.rename(columns={
        "Location": "station_id",
        "DateTime": "timestamp",
        "Temperature_C": "temperature",
        "Pressure_hPa": "pressure",
        "Humidity_Percent": "humidity",
    })
    qc_columns = [column for column in checked.columns if column not in canonical.columns]
    missing_qc_columns = [column for column in qc_columns if column not in result.columns]
    if missing_qc_columns:
        result = result.merge(
            checked[["station_id", "timestamp", *missing_qc_columns]],
            on=["station_id", "timestamp"],
            how="left",
        )
    detected_keys = pd.MultiIndex.from_frame(result[["station_id", "timestamp"]])
    checked_keys = pd.MultiIndex.from_frame(checked[["station_id", "timestamp"]])
    missing_rows = checked.loc[~checked_keys.isin(detected_keys)].copy()
    if not missing_rows.empty:
        missing_results = _build_qc_only_results(missing_rows)
        result = pd.concat([result, missing_results], ignore_index=True, sort=False)
    rule_anomaly = result[["qc_failed", "timestamp_gap_fail"]].fillna(False).any(axis=1)
    feature_anomaly = result[["temperature_rate_fail", "pressure_rate_fail", "humidity_rate_fail", "temperature_deviation_fail", "pressure_deviation_fail", "humidity_deviation_fail", "temperature_drift_fail", "pressure_drift_fail", "humidity_drift_fail", "persistence_fail", "thermodynamic_fail"]].fillna(False).any(axis=1)
    result["Rule_Anomaly"] = (rule_anomaly | feature_anomaly).astype(int)
    result["Final_Anomaly"] = ((result["Ensemble_Anomaly"].fillna(0).astype(bool)) | result["Rule_Anomaly"].astype(bool)).astype(int)
    result["Final_Score"] = result[["Ensemble_Score", "Rule_Anomaly"]].fillna(0).max(axis=1)
    result = add_context_and_diagnosis(result)
    LOGGER.info("Context and diagnosis completed")
    return add_operational_intelligence(result)


def _build_qc_only_results(rows: pd.DataFrame) -> pd.DataFrame:
    results = rows.copy().rename(columns={
        "station_id": "station_id",
        "timestamp": "timestamp",
    })
    results["Ensemble_Anomaly"] = 0
    results["Ensemble_Score"] = 0.0
    results["Model_Agreement"] = 0
    results["Rule_Anomaly"] = 1
    results["Final_Anomaly"] = 1
    results["Final_Score"] = 1.0
    results["IF_Anomaly"] = 0
    results["IF_Score"] = 0.0
    results["SHAP_Available"] = False
    results["SHAP_Top_Feature"] = "Unavailable"
    results["SHAP_Top_Contribution"] = 0.0
    results["SHAP_Note"] = "No model attribution: observation followed the QC fast path."
    return results


def run_csv(input_path: str | Path, output_path: str | Path) -> pd.DataFrame:
    data = pd.read_csv(input_path)
    result = run_pipeline(data)
    destination = resolve_project_path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    result.to_csv(destination, index=False)
    return result


def process_batch(data: pd.DataFrame, contamination: float = 0.02) -> list[dict[str, Any]]:
    """Return documented structured result sections for each scored observation."""
    results = run_pipeline(data, contamination=contamination)
    return [_structured_result(row) for _, row in results.iterrows()]


def process_observation(observation: dict[str, Any], history: pd.DataFrame | None = None) -> dict[str, Any]:
    """Process one canonical observation, reporting warm-up when history is insufficient."""
    parsed, errors = validate_observation(observation)
    if errors or parsed is None:
        return {"observation": None, "quality": {"passed": False, "errors": [asdict(error) for error in errors]}}
    current = pd.DataFrame([observation])
    source = pd.concat([history, current], ignore_index=True) if history is not None else current
    if len(source) < 6:
        checked = run_quality_control(canonicalize_observations(current)).iloc[0]
        return {
            "observation": asdict(parsed),
            "quality": {"passed": not bool(checked["qc_failed"]), "rules": [asdict(rule) for rule in checked["qc_results"]]},
            "anomaly": None,
            "status": "WARMUP",
        }
    return process_batch(source)[-1]


def _structured_result(row: pd.Series) -> dict[str, Any]:
    rules = row.get("qc_results", [])
    return {
        "observation": {
            "station_id": row.get("station_id"),
            "timestamp": row.get("timestamp"),
            "temperature": row.get("temperature"),
            "pressure": row.get("pressure"),
            "humidity": row.get("humidity"),
        },
        "quality": {
            "passed": not bool(row.get("qc_failed", False)),
            "rules": [asdict(rule) if hasattr(rule, "__dataclass_fields__") else rule for rule in rules],
        },
        "features": {name: row[name] for name in ("Temperature_Diff", "Humidity_Diff", "Pressure_Diff", "dew_point") if name in row},
        "anomaly": {
            "is_anomaly": bool(row.get("Final_Anomaly", row.get("Ensemble_Anomaly", False))),
            "score": float(row.get("Final_Score", row.get("Ensemble_Score", 0.0))),
            "model_version": "ensemble-batch-v1",
        },
        "context": {
            "event_type": row.get("event_type", "UNCERTAIN"),
            "temporal_evidence": {"persistence": row.get("temporal_persistence", 0.0)},
            "spatial_evidence": row.get("spatial_evidence", {"available": False}),
        },
        "diagnosis": {
            "root_cause": row.get("root_cause", "UNKNOWN"),
            "severity": row.get("severity", "UNKNOWN"),
            "confidence": float(row.get("confidence", 0.0)),
        },
        "explanation": {
            "summary": row.get("explanation", ""),
            "feature_contributions": {
                row.get("SHAP_Top_Feature"): float(row.get("SHAP_Top_Contribution", 0.0))
            } if bool(row.get("SHAP_Available", False)) else {},
            "available": bool(row.get("SHAP_Available", False)),
            "note": row.get("SHAP_Note", "Feature contribution only; not causal proof."),
        },
        "health": {"health_score": float(row.get("health_score", 0.0)), "health_status": row.get("health_status", "UNKNOWN"), "health_trend": row.get("health_trend", "unknown")},
        "maintenance": {"action": row.get("maintenance_recommendation", "No recommendation available")},
        "recovery": {
            "original_value": row.get("recovery_original_temperature", row.get("temperature")),
            "suggested_value": row.get("recovery_suggestion"),
            "status": row.get("recovery_status", "NOT_AVAILABLE"),
            "method": row.get("recovery_method", ""),
            "reason": row.get("recovery_reason", ""),
        },
    }
