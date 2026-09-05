from __future__ import annotations

from dataclasses import dataclass
from time import perf_counter
from typing import Iterator

import pandas as pd

from ..pipeline import run_pipeline


@dataclass(frozen=True)
class ReplayRecord:
    position: int
    total: int
    timestamp: pd.Timestamp
    processing_ms: float
    result: dict


def replay(data: pd.DataFrame) -> Iterator[ReplayRecord]:
    """Replay observations in timestamp order with measured batch latency."""
    ordered = data.sort_values("timestamp").reset_index(drop=True)
    total = len(ordered)
    for position in range(total):
        row = ordered.iloc[: position + 1]
        started = perf_counter()
        result = run_pipeline(row) if position >= 5 else pd.DataFrame()
        elapsed = (perf_counter() - started) * 1000
        latest = result.iloc[-1] if not result.empty else pd.Series({"timestamp": row["timestamp"].iloc[-1]})
        yield ReplayRecord(
            position=position + 1,
            total=total,
            timestamp=pd.Timestamp(row["timestamp"].iloc[-1]),
            processing_ms=elapsed,
            result=latest.to_dict(),
        )
