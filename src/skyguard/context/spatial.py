from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd


def evaluate_spatial_context(
    target: pd.Series,
    neighbors: pd.DataFrame,
    variable: str = "temperature",
    max_neighbors: int = 3,
) -> dict[str, Any]:
    """Compare a station with nearby observations without inventing neighbors."""
    required = {"latitude", "longitude", variable}
    if not required.issubset(target.index) or not required.issubset(neighbors.columns):
        return {"available": False, "reason": "Station coordinates or neighbor values are unavailable."}
    if pd.isna(target["latitude"]) or pd.isna(target["longitude"]):
        return {"available": False, "reason": "Target station coordinates are unavailable."}
    candidates = neighbors.dropna(subset=["latitude", "longitude", variable]).copy()
    candidates = candidates[candidates.get("station_id", pd.Series(index=candidates.index, dtype=str)) != target.get("station_id")]
    if candidates.empty:
        return {"available": False, "reason": "No neighboring station observations are available."}
    distances = _distance_km(
        float(target["latitude"]), float(target["longitude"]),
        candidates["latitude"].to_numpy(float), candidates["longitude"].to_numpy(float),
    )
    candidates["distance_km"] = distances
    candidates = candidates.sort_values("distance_km").head(max_neighbors)
    values = candidates[variable].astype(float)
    median = float(values.median())
    deviation = abs(float(target[variable]) - median)
    mad = float((values - median).abs().median())
    return {
        "available": True,
        "neighbor_count": len(candidates),
        "neighbor_station_ids": candidates.get("station_id", pd.Series(dtype=str)).tolist(),
        "median": median,
        "deviation": deviation,
        "mad": mad,
        "consensus": float((values - median).abs().le(max(1.0, 3 * mad)).mean()),
    }


def _distance_km(latitude: float, longitude: float, latitudes: np.ndarray, longitudes: np.ndarray) -> np.ndarray:
    earth_radius_km = 6371.0
    lat1, lat2 = np.radians(latitude), np.radians(latitudes)
    delta_lat = np.radians(latitudes - latitude)
    delta_lon = np.radians(longitudes - longitude)
    haversine = np.sin(delta_lat / 2) ** 2 + np.cos(lat1) * np.cos(lat2) * np.sin(delta_lon / 2) ** 2
    return earth_radius_km * 2 * np.arcsin(np.sqrt(haversine))
