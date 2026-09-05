from dataclasses import dataclass, field
from pathlib import Path


@dataclass(frozen=True)
class VariableThreshold:
    minimum: float
    maximum: float
    max_step_per_hour: float

    def validate(self, value: float) -> bool:
        return self.minimum <= value <= self.maximum


@dataclass(frozen=True)
class QCConfig:
    temperature: VariableThreshold = field(
        default_factory=lambda: VariableThreshold(
            minimum=-50.0,
            maximum=60.0,
            max_step_per_hour=12.0,
        )
    )
    pressure: VariableThreshold = field(
        default_factory=lambda: VariableThreshold(
            minimum=850.0,
            maximum=1100.0,
            max_step_per_hour=8.0,
        )
    )
    humidity: VariableThreshold = field(
        default_factory=lambda: VariableThreshold(
            minimum=0.0,
            maximum=100.0,
            max_step_per_hour=35.0,
        )
    )
    persistence_window: int = 4
    max_baseline_deviation: float = 10.0
    drift_window: int = 4
    drift_threshold: float = 5.0
    regional_shift_threshold: float = 3.0
    expected_interval_hours: float = 3.0
    dew_point_tolerance: float = 0.25


@dataclass(frozen=True)
class IsolationForestConfig:
    n_estimators: int = 300
    contamination: float = 0.02
    random_state: int = 42
    n_jobs: int = -1

    def __post_init__(self) -> None:
        if not 0 < self.contamination < 0.5:
            raise ValueError("contamination must be between 0 and 0.5")
        if self.n_estimators <= 0:
            raise ValueError("n_estimators must be positive")


@dataclass(frozen=True)
class FeatureFlagConfig:
    enable_spatial_validation: bool = False
    enable_shap_explanations: bool = False
    enable_sensor_health: bool = False
    enable_recovery: bool = False
    enable_lstm_autoencoder: bool = False


@dataclass(frozen=True)
class PathConfig:
    data_dir: Path = Path("data")
    processed_data_dir: Path = Path("data/processed")
    model_dir: Path = Path("models/trained")
    model_metadata_dir: Path = Path("models/metadata")
    output_dir: Path = Path("outputs/exports")
    evaluation_dir: Path = Path("outputs/evaluation")
    feature_dataset: Path = Path("data/processed/SkyGuard_features.csv")
    anomaly_results: Path = Path("outputs/exports/anomaly_detection_results.csv")
    bundled_results: Path = Path("outputs/exports/mvp_results.csv")


@dataclass(frozen=True)
class AppConfig:
    schema_version: str = "1.0"
    qc: QCConfig = field(default_factory=QCConfig)
    model: IsolationForestConfig = field(default_factory=IsolationForestConfig)
    features: FeatureFlagConfig = field(default_factory=FeatureFlagConfig)
    paths: PathConfig = field(default_factory=PathConfig)


DEFAULT_CONFIG = AppConfig()

