from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

import pandas as pd

from .scenarios import inject_anomaly, inject_isolated_fault, inject_regional_event
from .metrics import evaluate_detection
from ..ingestion.csv_loader import simulate_observations
from ..pipeline import run_pipeline
from ..config import DEFAULT_CONFIG
from ..utils.paths import resolve_project_path


def run_evaluation(output_path: str | Path = DEFAULT_CONFIG.paths.evaluation_dir / "latest.csv") -> dict:
    """Run a reproducible injected-scenario evaluation and persist row results."""
    clean = simulate_observations(stations=4, periods=40, seed=42)
    scenarios = [
        ("SPIKE", "temperature"),
        ("FROZEN_STUCK", "humidity"),
        ("DRIFT_BIAS", "pressure"),
        ("COMMUNICATION_MISSING", "temperature"),
    ]
    injected = clean.copy()
    injected["ground_truth"] = "NORMAL"
    for offset, (kind, variable) in enumerate(scenarios):
        station = f"AWS-{offset + 1:02d}"
        start = str(clean.loc[clean["station_id"].eq(station), "timestamp"].iloc[20])
        scenario = inject_isolated_fault(injected, station, start, kind, duration=4, variable=variable)
        injected["ground_truth"] = scenario["ground_truth"]
        for column in ["temperature", "pressure", "humidity"]:
            injected[column] = scenario[column]
    regional_start = str(clean["timestamp"].drop_duplicates().iloc[28])
    regional = inject_regional_event(injected, regional_start, duration=3)
    injected["ground_truth"] = regional["ground_truth"]
    for column in ["temperature", "pressure", "humidity"]:
        injected[column] = regional[column]
    started = perf_counter()
    results = run_pipeline(injected)
    total_latency_ms = (perf_counter() - started) * 1000
    results["processing_ms"] = total_latency_ms / max(len(results), 1)
    metrics = evaluate_detection(results)
    destination = resolve_project_path(output_path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    results.to_csv(destination, index=False)
    return {
        "run_at": datetime.now(timezone.utc).isoformat(),
        "rows": len(results),
        "scenarios": len(scenarios) + 1,
        "output": str(destination),
        "total_latency_ms": total_latency_ms,
        **metrics,
    }
