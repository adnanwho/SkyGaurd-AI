import pandas as pd
import pytest

from src.skyguard.engine import SkyGuardEngine, SkyGuardResult
from src.skyguard.ingestion.csv_loader import simulate_observations


def test_engine_process_returns_stable_result_contract():
    result = SkyGuardEngine().process(simulate_observations(stations=1, periods=10))

    assert isinstance(result, SkyGuardResult)
    assert result.summary["total_observations"] == 10
    assert {"station_id", "timestamp", "Final_Anomaly"}.issubset(result.observations.columns)
    assert result.summary["total_anomalies"] == len(result.anomalies)
    assert result.timings["total_ms"] >= 0


def test_engine_empty_input_returns_empty_result():
    result = SkyGuardEngine().process(pd.DataFrame())

    assert result.summary["total_observations"] == 0
    assert result.observations.empty
    assert result.anomalies.empty


def test_engine_invalid_schema_has_actionable_error():
    with pytest.raises(ValueError, match="Missing required observation columns"):
        SkyGuardEngine().process(pd.DataFrame({"station_id": ["AWS-01"]}))


def test_engine_calls_do_not_share_dataset_state():
    engine = SkyGuardEngine()
    first = engine.process(simulate_observations(stations=1, periods=10))
    second = engine.process(simulate_observations(stations=2, periods=10))

    assert first.summary["total_stations"] == 1
    assert second.summary["total_stations"] == 2
    assert len(first.observations) == 10
    assert len(second.observations) == 20