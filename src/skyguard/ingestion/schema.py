from dataclasses import dataclass, field
from datetime import datetime
from enum import StrEnum
from typing import Any


class WeatherVariable(StrEnum):
    TEMPERATURE = "temperature"
    PRESSURE = "pressure"
    HUMIDITY = "humidity"


class EventType(StrEnum):
    NORMAL = "NORMAL"
    SENSOR_FAULT = "SENSOR_FAULT"
    WEATHER_EVENT = "WEATHER_EVENT"
    UNCERTAIN = "UNCERTAIN"


class RootCause(StrEnum):
    NONE = "NONE"
    SPIKE = "SPIKE"
    FROZEN_STUCK = "FROZEN_STUCK"
    DRIFT_BIAS = "DRIFT_BIAS"
    COMMUNICATION_MISSING = "COMMUNICATION_MISSING"
    UNKNOWN = "UNKNOWN"


class Severity(StrEnum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    UNKNOWN = "UNKNOWN"


class HealthStatus(StrEnum):
    HEALTHY = "HEALTHY"
    WARNING = "WARNING"
    DEGRADING = "DEGRADING"
    CRITICAL = "CRITICAL"
    UNKNOWN = "UNKNOWN"


class RecoveryStatus(StrEnum):
    NOT_AVAILABLE = "NOT_AVAILABLE"
    NOT_REQUIRED = "NOT_REQUIRED"
    SUGGESTED = "SUGGESTED"
    PENDING_VALIDATION = "PENDING_VALIDATION"
    ACCEPTED = "ACCEPTED"
    REJECTED = "REJECTED"


class RuleSeverity(StrEnum):
    INFO = "INFO"
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"


class SchemaErrorCode(StrEnum):
    MISSING_FIELD = "MISSING_FIELD"
    INVALID_TYPE = "INVALID_TYPE"
    INVALID_VALUE = "INVALID_VALUE"


@dataclass(frozen=True)
class SchemaError:
    field: str
    code: SchemaErrorCode
    message: str


@dataclass(frozen=True)
class RawObservation:
    station_id: str
    timestamp: datetime
    temperature: float | None
    pressure: float | None
    humidity: float | None
    latitude: float | None = None
    longitude: float | None = None
    elevation: float | None = None


@dataclass(frozen=True)
class QCResult:
    rule_id: str
    passed: bool
    severity: RuleSeverity
    flag: str
    message: str


@dataclass(frozen=True)
class QualityResult:
    passed: bool
    rules: list[QCResult] = field(default_factory=list)


@dataclass(frozen=True)
class AnomalyResult:
    is_anomaly: bool
    score: float
    model_version: str = "unversioned"


@dataclass(frozen=True)
class ContextResult:
    event_type: EventType = EventType.UNCERTAIN
    temporal_evidence: dict[str, Any] = field(default_factory=dict)
    spatial_evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class DiagnosticResult:
    root_cause: RootCause = RootCause.UNKNOWN
    severity: Severity = Severity.UNKNOWN
    confidence: float = 0.0


@dataclass(frozen=True)
class ExplanationResult:
    summary: str = ""
    feature_contributions: dict[str, float] = field(default_factory=dict)


@dataclass(frozen=True)
class HealthResult:
    health_score: float = 100.0
    health_status: HealthStatus = HealthStatus.UNKNOWN
    health_trend: str = "unknown"


@dataclass(frozen=True)
class MaintenanceRecommendation:
    action: str = "No recommendation available"
    reason: str = ""


@dataclass(frozen=True)
class RecoverySuggestion:
    variable: WeatherVariable | None = None
    original_value: float | None = None
    suggested_value: float | None = None
    status: RecoveryStatus = RecoveryStatus.NOT_AVAILABLE
    method: str = ""
    reason: str = ""


@dataclass(frozen=True)
class ProcessedObservation:
    observation: RawObservation
    quality: QualityResult
    anomaly: AnomalyResult | None = None
    context: ContextResult = field(default_factory=ContextResult)
    diagnosis: DiagnosticResult = field(default_factory=DiagnosticResult)
    explanation: ExplanationResult = field(default_factory=ExplanationResult)
    health: HealthResult = field(default_factory=HealthResult)
    maintenance: MaintenanceRecommendation = field(default_factory=MaintenanceRecommendation)
    recovery: RecoverySuggestion = field(default_factory=RecoverySuggestion)


@dataclass(frozen=True)
class StationMetadata:
    station_id: str
    latitude: float
    longitude: float
    elevation: float | None = None
    name: str | None = None


def parse_timestamp(value: Any) -> datetime | None:
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        try:
            return datetime.fromisoformat(value)
        except ValueError:
            return None
    return None


def validate_observation(payload: dict[str, Any]) -> tuple[RawObservation | None, list[SchemaError]]:
    errors: list[SchemaError] = []
    required_fields = ("station_id", "timestamp", "temperature", "pressure", "humidity")

    for field_name in required_fields:
        if field_name not in payload:
            errors.append(
                SchemaError(
                    field=field_name,
                    code=SchemaErrorCode.MISSING_FIELD,
                    message=f"{field_name} is required",
                )
            )

    if errors:
        return None, errors

    station_id = payload["station_id"]
    if not isinstance(station_id, str) or not station_id.strip():
        errors.append(
            SchemaError("station_id", SchemaErrorCode.INVALID_VALUE, "station_id must be a non-empty string")
        )

    timestamp = parse_timestamp(payload["timestamp"])
    if timestamp is None:
        errors.append(
            SchemaError("timestamp", SchemaErrorCode.INVALID_TYPE, "timestamp must be a datetime or ISO datetime")
        )

    numeric_fields = ("temperature", "pressure", "humidity", "latitude", "longitude", "elevation")
    converted: dict[str, float | None] = {}
    for field_name in numeric_fields:
        value = payload.get(field_name)
        if value is None:
            converted[field_name] = None
            continue
        if isinstance(value, bool):
            errors.append(SchemaError(field_name, SchemaErrorCode.INVALID_TYPE, f"{field_name} must be numeric"))
            continue
        try:
            converted[field_name] = float(value)
        except (TypeError, ValueError):
            errors.append(SchemaError(field_name, SchemaErrorCode.INVALID_TYPE, f"{field_name} must be numeric"))

    if errors:
        return None, errors

    return (
        RawObservation(
            station_id=station_id.strip(),
            timestamp=timestamp,
            temperature=converted["temperature"],
            pressure=converted["pressure"],
            humidity=converted["humidity"],
            latitude=converted["latitude"],
            longitude=converted["longitude"],
            elevation=converted["elevation"],
        ),
        [],
    )


def validate_observation_dataframe(df: Any) -> list[SchemaError]:
    required_fields = ("station_id", "timestamp", "temperature", "pressure", "humidity")
    missing = [field_name for field_name in required_fields if field_name not in df.columns]
    return [
        SchemaError(
            field=field_name,
            code=SchemaErrorCode.MISSING_FIELD,
            message=f"{field_name} column is required",
        )
        for field_name in missing
    ]


WeatherTelemetryRecord = RawObservation
AnomalyType = RootCause
SensorType = WeatherVariable
validate_telemetry_dataframe = validate_observation_dataframe

