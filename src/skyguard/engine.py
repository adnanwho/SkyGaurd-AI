from __future__ import annotations

from dataclasses import dataclass, field
from time import perf_counter
from typing import Any

import pandas as pd

from .config import AppConfig, DEFAULT_CONFIG
from .ingestion.csv_loader import canonicalize_observations
from .pipeline import run_pipeline
from .utils.logging import get_logger


@dataclass(frozen=True)
class SkyGuardResult:
    """Stable output contract for batch processing and future adapters."""

    summary: dict[str, Any]
    observations: pd.DataFrame
    anomalies: pd.DataFrame
    sensor_health: pd.DataFrame
    diagnostics: pd.DataFrame
    metrics: dict[str, Any] = field(default_factory=dict)
    timings: dict[str, float] = field(default_factory=dict)


class SkyGuardEngine:
    """Canonical programmatic boundary for the existing SkyGuard pipeline."""

    def __init__(self, config: AppConfig = DEFAULT_CONFIG) -> None:
        self.config = config
        self.logger = get_logger("skyguard.engine")

    def process(self, data: pd.DataFrame) -> SkyGuardResult:
        """Process canonical or legacy observations and return a structured result."""
        if not isinstance(data, pd.DataFrame):
            raise TypeError("SkyGuardEngine.process expects a pandas DataFrame")
        if data.empty:
            return self._empty_result()

        self.logger.info("Input received: %s rows", len(data))
        started = perf_counter()
        canonical = canonicalize_observations(data)
        self.logger.info("Rows validated: %s", len(canonical))
        processed = run_pipeline(canonical, contamination=self.config.model.contamination)
        elapsed_ms = (perf_counter() - started) * 1000
        self.logger.info("Pipeline completed: %s rows in %.2f ms", len(processed), elapsed_ms)
        return self._build_result(processed, elapsed_ms)

    def _build_result(self, processed: pd.DataFrame, elapsed_ms: float) -> SkyGuardResult:
        anomaly_column = "Final_Anomaly" if "Final_Anomaly" in processed else "Ensemble_Anomaly"
        anomaly_mask = processed[anomaly_column].fillna(0).astype(bool)
        anomalies = processed.loc[anomaly_mask].copy()
        latest = processed.sort_values("timestamp").groupby("station_id", as_index=False).tail(1)
        severity = processed.loc[anomaly_mask, "severity"] if "severity" in processed else pd.Series(dtype=str)
        summary = {
            "total_observations": int(len(processed)),
            "total_stations": int(processed["station_id"].nunique()),
            "total_anomalies": int(anomaly_mask.sum()),
            "anomaly_rate": float(anomaly_mask.mean()) if len(processed) else 0.0,
            "high_severity_count": int(severity.eq("HIGH").sum()),
            "medium_severity_count": int(severity.eq("MEDIUM").sum()),
            "low_severity_count": int(severity.eq("LOW").sum()),
            "processing_time_ms": elapsed_ms,
        }
        diagnostics_columns = [
            column for column in ["timestamp", "station_id", "event_type", "root_cause", "severity", "confidence", "explanation"]
            if column in anomalies.columns
        ]
        return SkyGuardResult(
            summary=summary,
            observations=processed,
            anomalies=anomalies,
            sensor_health=latest,
            diagnostics=anomalies[diagnostics_columns].copy(),
            metrics={},
            timings={"total_ms": elapsed_ms},
        )

    def _empty_result(self) -> SkyGuardResult:
        empty = pd.DataFrame()
        return SkyGuardResult(
            summary={
                "total_observations": 0,
                "total_stations": 0,
                "total_anomalies": 0,
                "anomaly_rate": 0.0,
                "high_severity_count": 0,
                "medium_severity_count": 0,
                "low_severity_count": 0,
                "processing_time_ms": 0.0,
            },
            observations=empty,
            anomalies=empty.copy(),
            sensor_health=empty.copy(),
            diagnostics=empty.copy(),
            timings={"total_ms": 0.0},
        )