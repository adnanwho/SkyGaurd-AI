import pandas as pd

from src.skyguard.preprocessing.quality_control import run_quality_control


def test_quality_control_preserves_multiple_structured_rule_results():
    observations = pd.DataFrame({
        "station_id": ["AWS-01", "AWS-01"],
        "timestamp": pd.to_datetime(["2026-01-01 00:00", "2026-01-01 06:00"]),
        "temperature": [25.0, 90.0],
        "pressure": [1008.0, 1008.0],
        "humidity": [50.0, 50.0],
    })

    result = run_quality_control(observations)
    failed = [rule.flag for rule in result.loc[1, "qc_results"] if not rule.passed]

    assert result.loc[1, "timestamp_gap_fail"]
    assert "COMMUNICATION_GAP" in failed
    assert "PHYSICAL_RANGE_VIOLATION" in failed
    assert len(result.loc[1, "qc_results"]) >= 7


def test_quality_control_accepts_configured_regular_interval():
    observations = pd.DataFrame({
        "station_id": ["AWS-01", "AWS-01"],
        "timestamp": pd.to_datetime(["2026-01-01 00:00", "2026-01-01 03:00"]),
        "temperature": [25.0, 25.1],
        "pressure": [1008.0, 1008.1],
        "humidity": [50.0, 50.1],
    })

    result = run_quality_control(observations)

    assert not result["timestamp_gap_fail"].any()


def test_quality_control_tracks_persistence_for_each_variable():
    observations = pd.DataFrame({
        "station_id": ["AWS-01"] * 5,
        "timestamp": pd.date_range("2026-01-01", periods=5, freq="3h"),
        "temperature": [20.0, 20.1, 20.2, 20.3, 20.4],
        "pressure": [1000.0] * 5,
        "humidity": [50.0] * 5,
    })

    result = run_quality_control(observations)

    assert result.loc[4, "pressure_persistence_fail"]
    assert result.loc[4, "humidity_persistence_fail"]
    assert result.loc[4, "persistence_fail"]


def test_quality_control_flags_large_recent_baseline_deviation():
    observations = pd.DataFrame({
        "station_id": ["AWS-01"] * 5,
        "timestamp": pd.date_range("2026-01-01", periods=5, freq="3h"),
        "temperature": [20.0, 20.1, 20.2, 20.3, 45.0],
        "pressure": [1000.0] * 5,
        "humidity": [50.0] * 5,
    })

    result = run_quality_control(observations)

    assert result.loc[4, "temperature_deviation_fail"]


def test_quality_control_identifies_sustained_drift():
    observations = pd.DataFrame({
        "station_id": ["AWS-01"] * 6,
        "timestamp": pd.date_range("2026-01-01", periods=6, freq="3h"),
        "temperature": [20.0, 22.0, 24.0, 26.0, 28.0, 30.0],
        "pressure": [1000.0] * 6,
        "humidity": [50.0] * 6,
    })

    result = run_quality_control(observations)

    assert result.loc[4, "temperature_drift_fail"]
