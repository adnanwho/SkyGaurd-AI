import pytest

from src.skyguard.config import DEFAULT_CONFIG, IsolationForestConfig


def test_default_config_uses_documented_paths():
    assert DEFAULT_CONFIG.paths.feature_dataset.as_posix() == "data/processed/SkyGuard_features.csv"
    assert DEFAULT_CONFIG.paths.anomaly_results.as_posix() == "outputs/exports/anomaly_detection_results.csv"


def test_variable_threshold_validation():
    assert DEFAULT_CONFIG.qc.temperature.validate(35.0)
    assert not DEFAULT_CONFIG.qc.temperature.validate(80.0)
    assert DEFAULT_CONFIG.qc.humidity.validate(100.0)


def test_isolation_forest_config_rejects_invalid_contamination():
    with pytest.raises(ValueError):
        IsolationForestConfig(contamination=0.0)

    with pytest.raises(ValueError):
        IsolationForestConfig(contamination=0.9)
