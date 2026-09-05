from __future__ import annotations

import pandas as pd

from ..ingestion.schema import RootCause


def inject_anomaly(
    data: pd.DataFrame,
    station_id: str,
    start: str,
    kind: RootCause | str,
    duration: int = 4,
    variable: str = "temperature",
) -> pd.DataFrame:
    """Inject a labeled, reproducible scenario without changing the input frame."""
    frame = data.copy()
    if "ground_truth" not in frame:
        frame["ground_truth"] = "NORMAL"
    mask = (frame["station_id"] == station_id) & (frame["timestamp"] >= pd.Timestamp(start))
    indices = frame.index[mask][:duration]
    if len(indices) == 0:
        raise ValueError("No observations match the requested station and start time")
    label = RootCause(str(kind)).value if str(kind) in RootCause._value2member_map_ else str(kind)
    frame.loc[indices, "ground_truth"] = label
    if kind in (RootCause.SPIKE, "SPIKE"):
        frame.loc[indices, variable] = frame.loc[indices, variable] + (18.0 if variable == "temperature" else 25.0)
    elif kind in (RootCause.FROZEN_STUCK, "FROZEN_STUCK"):
        frame.loc[indices, variable] = frame.loc[indices[0], variable]
    elif kind in (RootCause.DRIFT_BIAS, "DRIFT_BIAS"):
        frame.loc[indices, variable] = frame.loc[indices, variable] + 2.0 * (indices.to_numpy() - indices[0] + 1)
    elif kind in (RootCause.COMMUNICATION_MISSING, "COMMUNICATION_MISSING"):
        frame.loc[indices, variable] = pd.NA
    else:
        raise ValueError(f"Unsupported anomaly kind: {kind}")
    return frame


def inject_isolated_fault(
    data: pd.DataFrame,
    station_id: str,
    start: str,
    kind: RootCause | str = RootCause.SPIKE,
    duration: int = 4,
    variable: str = "temperature",
) -> pd.DataFrame:
    """Inject a fault into one station while preserving neighboring observations."""
    return inject_anomaly(data, station_id, start, kind, duration, variable)


def inject_regional_event(
    data: pd.DataFrame,
    start: str,
    duration: int = 4,
    variable: str = "temperature",
    magnitude: float = 5.0,
) -> pd.DataFrame:
    """Inject the same weather signal into all stations at the same timestamps."""
    frame = data.copy()
    if "ground_truth" not in frame:
        frame["ground_truth"] = "NORMAL"
    mask = frame["timestamp"] >= pd.Timestamp(start)
    indices = frame.index[mask].unique()
    timestamps = sorted(frame.loc[indices, "timestamp"].unique())[:duration]
    if not timestamps:
        raise ValueError("No observations match the requested regional-event start")
    selected = frame[frame["timestamp"].isin(timestamps)].index
    frame.loc[selected, "ground_truth"] = "WEATHER_EVENT"
    frame.loc[selected, variable] = frame.loc[selected, variable] + magnitude
    return frame
