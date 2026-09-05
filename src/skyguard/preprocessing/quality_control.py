from __future__ import annotations

import numpy as np
import pandas as pd

from ..config import DEFAULT_CONFIG
from ..ingestion.schema import QCResult, RuleSeverity


def run_quality_control(data: pd.DataFrame) -> pd.DataFrame:
    frame = data.copy().sort_values(["station_id", "timestamp"]).reset_index(drop=True)
    for column in ["temperature", "pressure", "humidity"]:
        threshold = getattr(DEFAULT_CONFIG.qc, column)
        frame[f"{column}_range_fail"] = ~frame[column].between(threshold.minimum, threshold.maximum)
        previous = frame.groupby("station_id")[column].shift(1)
        delta_hours = frame.groupby("station_id")["timestamp"].diff().dt.total_seconds().div(3600).fillna(1)
        frame[f"{column}_rate_fail"] = (frame[column] - previous).abs() > threshold.max_step_per_hour * delta_hours
        rolling_baseline = frame.groupby("station_id")[column].transform(
            lambda values: values.shift(1).rolling(DEFAULT_CONFIG.qc.persistence_window, min_periods=DEFAULT_CONFIG.qc.persistence_window).median()
        )
        frame[f"{column}_deviation_fail"] = (frame[column] - rolling_baseline).abs() > DEFAULT_CONFIG.qc.max_baseline_deviation
        frame[f"{column}_persistence_fail"] = frame.groupby("station_id")[column].transform(
            lambda values: values.rolling(DEFAULT_CONFIG.qc.persistence_window, min_periods=DEFAULT_CONFIG.qc.persistence_window).std()
        ).fillna(1) < 1e-6
        def sustained_drift(values: pd.Series) -> pd.Series:
            deltas = values.diff()
            cumulative = deltas.rolling(DEFAULT_CONFIG.qc.drift_window, min_periods=DEFAULT_CONFIG.qc.drift_window).sum().abs()
            direction = deltas.rolling(DEFAULT_CONFIG.qc.drift_window, min_periods=DEFAULT_CONFIG.qc.drift_window).apply(
                lambda window: float(np.all(window > 0) or np.all(window < 0)), raw=True
            )
            return (cumulative > DEFAULT_CONFIG.qc.drift_threshold) & direction.eq(1)

        frame[f"{column}_drift_fail"] = frame.groupby("station_id")[column].transform(sustained_drift)
    frame["missing_fail"] = frame[["temperature", "pressure", "humidity"]].isna().any(axis=1)
    frame["timestamp_gap_fail"] = frame.groupby("station_id")["timestamp"].diff().dt.total_seconds().div(3600).gt(DEFAULT_CONFIG.qc.expected_interval_hours).fillna(False)
    frame["duplicate_fail"] = frame.duplicated(["station_id", "timestamp"], keep=False)
    frame["persistence_fail"] = frame[
        [f"{column}_persistence_fail" for column in ["temperature", "pressure", "humidity"]]
    ].any(axis=1)
    frame["qc_failed"] = frame.filter(regex="(_fail)$").any(axis=1)
    frame["qc_flags"] = frame.filter(regex="(_fail)$").apply(
        lambda row: ",".join(row.index[row.fillna(False)]), axis=1
    )
    frame["dew_point"] = _dew_point(frame["temperature"], frame["humidity"])
    frame["thermodynamic_fail"] = frame["dew_point"] > frame["temperature"] + DEFAULT_CONFIG.qc.dew_point_tolerance
    frame["qc_failed"] = frame["qc_failed"] | frame["thermodynamic_fail"]
    frame["qc_results"] = frame.apply(_build_rule_results, axis=1)
    return frame.sort_values(["timestamp", "station_id"]).reset_index(drop=True)


def _build_rule_results(row: pd.Series) -> list[QCResult]:
    checks = [
        ("QC-02-MISSING", bool(row["missing_fail"]), "MISSING_OBSERVATION", "One or more required sensor values are missing."),
        ("QC-02-GAP", bool(row["timestamp_gap_fail"]), "COMMUNICATION_GAP", "The station has an irregular timestamp gap."),
        ("QC-03-RANGE", bool(row[["temperature_range_fail", "pressure_range_fail", "humidity_range_fail"]].any()), "PHYSICAL_RANGE_VIOLATION", "A sensor value is outside its configured physical range."),
        ("QC-04-RATE", bool(row[["temperature_rate_fail", "pressure_rate_fail", "humidity_rate_fail"]].any()), "EXCESSIVE_RATE", "A sensor changed faster than its configured rate limit."),
        ("QC-04-DEVIATION", bool(row[["temperature_deviation_fail", "pressure_deviation_fail", "humidity_deviation_fail"]].any()), "BASELINE_DEVIATION", "A sensor value differs materially from its recent station baseline."),
        ("QC-04-DRIFT", bool(row[["temperature_drift_fail", "pressure_drift_fail", "humidity_drift_fail"]].any()), "DRIFT_BIAS", "A sensor shows sustained movement away from its recent baseline."),
        ("QC-05-PERSISTENCE", bool(row["persistence_fail"]), "PERSISTENCE", "A sensor value remained unchanged across the persistence window."),
        ("QC-06-DEWPOINT", bool(row["thermodynamic_fail"]), "THERMODYNAMIC_INCONSISTENCY", "Calculated dew point is above temperature."),
        ("QC-07-DUPLICATE", bool(row["duplicate_fail"]), "DUPLICATE_OBSERVATION", "The station and timestamp occur more than once."),
    ]
    results: list[QCResult] = []
    for rule_id, failed, flag, message in checks:
        results.append(QCResult(rule_id=rule_id, passed=not failed, severity=RuleSeverity.HIGH if failed else RuleSeverity.INFO, flag=flag if failed else "PASS", message=message if failed else "Rule passed."))
    return results


def _dew_point(temperature: pd.Series, humidity: pd.Series) -> pd.Series:
    safe_humidity = humidity.clip(lower=1, upper=100)
    gamma = np.log(safe_humidity / 100) + (17.625 * temperature / (243.04 + temperature))
    return 243.04 * gamma / (17.625 - gamma)
