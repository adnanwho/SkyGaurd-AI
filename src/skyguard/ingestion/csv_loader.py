from __future__ import annotations

from pathlib import Path
from typing import Iterable

import numpy as np
import pandas as pd


LEGACY_COLUMNS = {
    "Location": "station_id",
    "DateTime": "timestamp",
    "Time": "timestamp",
    "Temperature_C": "temperature",
    "Pressure_hPa": "pressure",
    "Humidity_Percent": "humidity",
}


def canonicalize_observations(data: pd.DataFrame) -> pd.DataFrame:
    """Return a copy using the documented observation column names."""
    frame = data.rename(columns=LEGACY_COLUMNS).copy()
    required = ["station_id", "timestamp", "temperature", "pressure", "humidity"]
    missing = [column for column in required if column not in frame.columns]
    if missing:
        raise ValueError(f"Missing required observation columns: {missing}")
    frame["timestamp"] = pd.to_datetime(frame["timestamp"], errors="coerce")
    for column in ["temperature", "pressure", "humidity"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if frame["timestamp"].isna().any():
        raise ValueError("Observation data contains invalid timestamps")
    frame["station_id"] = frame["station_id"].astype(str).str.strip()
    return frame.sort_values(["timestamp", "station_id"]).reset_index(drop=True)


def load_observations(paths: Iterable[str | Path]) -> pd.DataFrame:
    frames = [canonicalize_observations(pd.read_csv(path)) for path in paths]
    if not frames:
        raise ValueError("At least one input path is required")
    return canonicalize_observations(pd.concat(frames, ignore_index=True))


def to_legacy_columns(data: pd.DataFrame) -> pd.DataFrame:
    frame = canonicalize_observations(data)
    legacy = frame.rename(columns={
        "station_id": "Location",
        "timestamp": "DateTime",
        "temperature": "Temperature_C",
        "pressure": "Pressure_hPa",
        "humidity": "Humidity_Percent",
    })
    if "Pressure_Missing" not in legacy:
        legacy["Pressure_Missing"] = legacy["Pressure_hPa"].isna().astype(int)
    return legacy


def simulate_observations(
    stations: int = 4,
    periods: int = 96,
    start: str = "2026-01-01",
    frequency: str = "3h",
    seed: int = 42,
) -> pd.DataFrame:
    """Create deterministic multi-station weather observations for demos/tests."""
    if stations < 1 or periods < 8:
        raise ValueError("stations must be positive and periods must be at least 8")
    rng = np.random.default_rng(seed)
    timestamps = pd.date_range(start=start, periods=periods, freq=frequency)
    rows: list[dict[str, object]] = []
    for station_index in range(stations):
        station = f"AWS-{station_index + 1:02d}"
        phase = station_index * 0.35
        latitude = 20.0 + station_index * 0.15
        longitude = 77.0 + station_index * 0.15
        for index, timestamp in enumerate(timestamps):
            daily = np.sin((index / 8.0) + phase)
            rows.append({
                "station_id": station,
                "timestamp": timestamp,
                "latitude": latitude,
                "longitude": longitude,
                "temperature": 28.0 + 4.0 * daily + rng.normal(0, 0.35),
                "pressure": 1008.0 + 3.0 * np.cos((index / 12.0) + phase) + rng.normal(0, 0.25),
                "humidity": float(np.clip(62.0 - 15.0 * daily + rng.normal(0, 1.2), 10, 98)),
            })
    return canonicalize_observations(pd.DataFrame(rows))
