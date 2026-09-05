import pandas as pd

from src.skyguard.evaluation.scenarios import inject_anomaly, inject_regional_event
from src.skyguard.evaluation.metrics import evaluate_detection
from src.skyguard.evaluation.runner import run_evaluation
from src.skyguard.explainability.explanations import explain_observation
from src.skyguard.ingestion.csv_loader import simulate_observations
from src.skyguard.pipeline import process_batch, process_observation, run_pipeline
from src.skyguard.replay.engine import replay
from src.skyguard.context.temporal import score_sequences, temporal_model_status


def test_simulation_injection_and_pipeline_produce_traceable_results():
    observations = simulate_observations(stations=3, periods=24)
    injected = inject_anomaly(observations, "AWS-01", str(observations["timestamp"].iloc[12]), "SPIKE", duration=2)
    result = run_pipeline(injected)
    assert len(result) > 0
    assert {"event_type", "root_cause", "health_score", "explanation"}.issubset(result.columns)
    assert result["station_id"].nunique() == 3


def test_evaluation_returns_real_metrics():
    result = pd.DataFrame({"ground_truth": ["NORMAL", "SPIKE", "NORMAL"], "Ensemble_Anomaly": [0, 1, 1]})
    metrics = evaluate_detection(result)
    assert metrics["true_positives"] == 1
    assert metrics["false_positives"] == 1
    assert metrics["recall"] == 1.0
    assert metrics["false_positive_rate"] == 0.5
    assert metrics["false_negative_rate"] == 0.0


def test_optional_explanation_and_replay_have_explicit_fallbacks():
    observations = simulate_observations(stations=1, periods=10)
    result = run_pipeline(observations)
    explanation = explain_observation(result.iloc[-1])
    records = list(replay(observations.iloc[:8]))
    assert explanation["available"] is False
    assert len(records) == 8
    assert all(record.processing_ms >= 0 for record in records)


def test_evaluation_runner_persists_reproducible_result(tmp_path):
    summary = run_evaluation(tmp_path / "evaluation.csv")
    assert summary["rows"] > 0
    assert summary["scenarios"] == 5
    assert summary["weather_event_recall"] > 0
    assert (tmp_path / "evaluation.csv").exists()


def test_structured_pipeline_api_exposes_documented_sections():
    observations = simulate_observations(stations=1, periods=10)
    structured = process_batch(observations)
    assert {"observation", "quality", "features", "anomaly", "context", "diagnosis", "health", "maintenance", "recovery"}.issubset(structured[-1])

    warmup = process_observation(observations.iloc[0].to_dict())
    assert warmup["status"] == "WARMUP"


def test_regional_event_changes_all_stations_and_preserves_coordinates():
    observations = simulate_observations(stations=3, periods=12)
    start = str(observations["timestamp"].drop_duplicates().iloc[8])
    injected = inject_regional_event(observations, start, duration=2)
    selected = injected[injected["ground_truth"] == "WEATHER_EVENT"]
    assert selected["station_id"].nunique() == 3
    assert selected["latitude"].notna().all()


def test_missing_observations_follow_qc_fast_path_into_final_results():
    observations = simulate_observations(stations=2, periods=12)
    injected = inject_anomaly(
        observations,
        "AWS-01",
        str(observations["timestamp"].iloc[6]),
        "COMMUNICATION_MISSING",
        duration=2,
    )
    result = run_pipeline(injected)
    missing = result[result["missing_fail"]]
    assert len(result) == len(injected)
    assert missing["Final_Anomaly"].eq(1).all()
    assert missing["root_cause"].eq("COMMUNICATION_MISSING").all()


def test_scored_rows_include_shap_attribution_when_dependency_is_available():
    observations = simulate_observations(stations=1, periods=12)
    result = run_pipeline(observations)
    scored = result[result["SHAP_Available"]]
    assert not scored.empty
    assert scored["SHAP_Top_Feature"].notna().all()


def test_lstm_module_reports_explicit_optional_status():
    status = temporal_model_status()
    assert status.method == "lstm_autoencoder"
    if not status.available:
        result = score_sequences(pd.DataFrame({"temperature": [1.0, 2.0]}))
        assert result["available"] is False
