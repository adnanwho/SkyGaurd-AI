from __future__ import annotations

import pandas as pd


def add_operational_intelligence(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy().sort_values(["station_id", "timestamp"]).reset_index(drop=True)
    anomaly_column = "Final_Anomaly" if "Final_Anomaly" in frame.columns else "Ensemble_Anomaly"
    anomaly_penalty = frame[anomaly_column].astype(float) * 12.0
    qc_penalty = frame["qc_failed"].astype(float) * 4.0
    recovery = (frame[anomaly_column].eq(0) & frame["qc_failed"].eq(False)).astype(float) * 2.0
    frame["health_score"] = (
        100 - (anomaly_penalty + qc_penalty - recovery)
        .groupby(frame["station_id"])
        .cumsum()
    ).clip(0, 100)
    frame["health_trend"] = frame.groupby("station_id")["health_score"].diff().fillna(0).map(
        lambda value: "improving" if value > 0 else "degrading" if value < 0 else "stable"
    )
    frame["health_status"] = pd.cut(frame["health_score"], [-1, 40, 70, 90, 101], labels=["CRITICAL", "DEGRADING", "WARNING", "HEALTHY"]).astype(str)
    frame["maintenance_recommendation"] = "No action required"
    frame.loc[frame["root_cause"] == "COMMUNICATION_MISSING", "maintenance_recommendation"] = "Inspect telemetry link and station power."
    frame.loc[frame["root_cause"] == "FROZEN_STUCK", "maintenance_recommendation"] = "Inspect sensor for a stuck or obstructed probe."
    frame.loc[frame["root_cause"].isin(["SPIKE", "UNKNOWN"]), "maintenance_recommendation"] = "Review station calibration and recent observations."
    original_temperature = frame["temperature"].copy()
    frame["recovery_suggestion"] = frame["temperature"].groupby(frame["station_id"]).transform(
        lambda values: values.interpolate(limit_direction="both")
    )
    frame["recovery_original_temperature"] = original_temperature
    frame["recovery_method"] = "temporal interpolation"
    frame["recovery_status"] = "NOT_REQUIRED"
    frame.loc[frame["temperature"].isna(), "recovery_status"] = "SUGGESTED"
    frame.loc[frame["temperature"].isna(), "recovery_reason"] = "Temperature is missing; interpolated value is offered for review."
    frame["recovery_reason"] = frame["recovery_reason"].fillna("Original observation retained; no correction required.")
    return frame.sort_values(["timestamp", "station_id"]).reset_index(drop=True)
