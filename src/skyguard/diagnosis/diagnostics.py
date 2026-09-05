from __future__ import annotations

import pandas as pd

from ..config import DEFAULT_CONFIG
from ..context.spatial import evaluate_spatial_context


def add_context_and_diagnosis(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy().sort_values(["timestamp", "station_id"]).reset_index(drop=True)
    anomaly_column = "Final_Anomaly" if "Final_Anomaly" in frame.columns else "Ensemble_Anomaly"
    spatial_records = []
    for _, row in frame.iterrows():
        same_time = frame[frame["timestamp"].eq(row["timestamp"])]
        spatial = evaluate_spatial_context(row, same_time)
        spatial_records.append(spatial)
    frame["spatial_available"] = [item["available"] for item in spatial_records]
    frame["regional_temperature"] = [item.get("median") for item in spatial_records]
    frame["spatial_deviation"] = [item.get("deviation") for item in spatial_records]
    frame["neighbor_consensus"] = [item.get("consensus", 0.0) for item in spatial_records]
    frame["spatial_evidence"] = spatial_records
    frame["spatial_deviation"] = frame["spatial_deviation"].fillna(0.0)
    regional_series = frame.groupby("timestamp")["temperature"].median().sort_index()
    regional_shift = regional_series.diff().abs()
    frame["regional_shift"] = frame["timestamp"].map(regional_shift).fillna(0.0)
    frame["regional_event_signal"] = frame["regional_shift"] >= DEFAULT_CONFIG.qc.regional_shift_threshold
    frame.loc[frame["regional_event_signal"], "Final_Anomaly"] = 1
    frame.loc[frame["regional_event_signal"], "Final_Score"] = frame.loc[frame["regional_event_signal"], "Final_Score"].clip(lower=0.65)
    anomaly_signal = frame[anomaly_column].eq(1) | frame["regional_event_signal"]
    frame["temporal_persistence"] = frame.groupby("station_id")[anomaly_column].transform(
        lambda values: values.rolling(3, min_periods=1).sum()
    )
    frame["event_type"] = "NORMAL"
    frame.loc[anomaly_signal & (frame["spatial_deviation"] >= 8), "event_type"] = "SENSOR_FAULT"
    regional_event = (frame["spatial_deviation"] < 8) & ((frame["neighbor_consensus"] >= 0.5) | frame["regional_event_signal"])
    frame.loc[anomaly_signal & regional_event, "event_type"] = "WEATHER_EVENT"
    frame.loc[anomaly_signal & (frame["event_type"] == "NORMAL"), "event_type"] = "UNCERTAIN"
    frame["root_cause"] = "NONE"
    frame.loc[frame["missing_fail"], "root_cause"] = "COMMUNICATION_MISSING"
    frame.loc[frame["persistence_fail"] & ~frame["missing_fail"], "root_cause"] = "FROZEN_STUCK"
    frame.loc[(frame["root_cause"] == "NONE") & frame[["temperature_drift_fail", "pressure_drift_fail", "humidity_drift_fail"]].any(axis=1), "root_cause"] = "DRIFT_BIAS"
    frame.loc[(frame["root_cause"] == "NONE") & frame[["temperature_deviation_fail", "pressure_deviation_fail", "humidity_deviation_fail"]].any(axis=1), "root_cause"] = "SPIKE"
    frame.loc[(frame["root_cause"] == "NONE") & (frame["temperature_rate_fail"] | frame["temperature_range_fail"]), "root_cause"] = "SPIKE"
    frame.loc[(frame["root_cause"] == "NONE") & (frame[anomaly_column] == 1), "root_cause"] = "UNKNOWN"
    score_column = "Final_Score" if "Final_Score" in frame.columns else "Ensemble_Score"
    frame["severity"] = pd.cut(frame[score_column], [-0.01, 0.5, 0.7, 0.85, 1.01], labels=["LOW", "MEDIUM", "HIGH", "CRITICAL"]).astype(str)
    frame.loc[frame[anomaly_column] == 0, "severity"] = "LOW"
    frame["confidence"] = (0.45 + 0.15 * frame["Model_Agreement"] + 0.1 * (frame["neighbor_consensus"] >= 0.5)).clip(0, 1).round(3)
    frame["explanation"] = frame.apply(_explanation, axis=1)
    return frame


def _explanation(row: pd.Series) -> str:
    anomaly = row.get("Final_Anomaly", row.get("Ensemble_Anomaly", 0))
    if anomaly == 0:
        return "Observation is consistent with the learned baseline and quality checks."
    if row["event_type"] == "SENSOR_FAULT":
        return "Station differs sharply from nearby stations while the ensemble models agree on an anomaly."
    if row["event_type"] == "WEATHER_EVENT":
        return "Several stations show similar behavior, suggesting a regional weather event."
    return f"Anomaly detected with model agreement {int(row['Model_Agreement'])}/4 and score {row.get('Final_Score', row['Ensemble_Score']):.2f}."
