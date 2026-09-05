from datetime import datetime

from src.skyguard.ingestion.schema import (
    EventType,
    RawObservation,
    RootCause,
    SchemaErrorCode,
    validate_observation,
)


def test_validate_observation_accepts_canonical_payload():
    observation, errors = validate_observation(
        {
            "station_id": " AWS-01 ",
            "timestamp": "2026-01-01T12:00:00",
            "temperature": "31.4",
            "pressure": 1008.2,
            "humidity": 61,
        }
    )

    assert errors == []
    assert observation == RawObservation(
        station_id="AWS-01",
        timestamp=datetime(2026, 1, 1, 12, 0, 0),
        temperature=31.4,
        pressure=1008.2,
        humidity=61.0,
    )


def test_validate_observation_reports_missing_required_fields():
    observation, errors = validate_observation({"station_id": "AWS-01"})

    assert observation is None
    assert {error.field for error in errors} == {"timestamp", "temperature", "pressure", "humidity"}
    assert all(error.code == SchemaErrorCode.MISSING_FIELD for error in errors)


def test_validate_observation_rejects_invalid_timestamp_and_station():
    observation, errors = validate_observation(
        {
            "station_id": "",
            "timestamp": "not-a-date",
            "temperature": 31.4,
            "pressure": 1008.2,
            "humidity": 61,
        }
    )

    assert observation is None
    assert {error.field for error in errors} == {"station_id", "timestamp"}


def test_validate_observation_rejects_non_numeric_sensor_values():
    observation, errors = validate_observation(
        {
            "station_id": "AWS-01",
            "timestamp": "2026-01-01T12:00:00",
            "temperature": "hot",
            "pressure": 1008.2,
            "humidity": False,
        }
    )

    assert observation is None
    assert {error.field for error in errors} == {"temperature", "humidity"}


def test_canonical_enums_match_documented_terms():
    assert EventType.SENSOR_FAULT == "SENSOR_FAULT"
    assert RootCause.FROZEN_STUCK == "FROZEN_STUCK"

