import argparse
import pandas as pd

from src.skyguard.config import DEFAULT_CONFIG
from src.skyguard.evaluation.metrics import evaluate_detection
from src.skyguard.evaluation.runner import run_evaluation
from src.skyguard.ingestion.csv_loader import simulate_observations
from src.skyguard.detection.baseline import score_with_baseline, train_baseline
from src.skyguard.engine import SkyGuardEngine
from src.skyguard.context.temporal import temporal_model_status, train_lstm_autoencoder
from src.skyguard.utils.paths import resolve_project_path


def main(argv=None):
    parser = argparse.ArgumentParser(description="Run the SkyGuard AI local MVP pipeline")
    parser.add_argument("--input", default=str(resolve_project_path("data/processed/SkyGuard_clean_3hourly.csv")))
    parser.add_argument("--output", default=str(DEFAULT_CONFIG.paths.anomaly_results))
    parser.add_argument("--simulate", action="store_true", help="Use deterministic simulated observations")
    parser.add_argument("--train-baseline", action="store_true", help="Train and persist a clean baseline model")
    parser.add_argument("--score-baseline", action="store_true", help="Score input with the persisted clean baseline")
    parser.add_argument("--evaluate", action="store_true", help="Run the reproducible injected-scenario evaluation")
    parser.add_argument("--lstm-status", action="store_true", help="Show optional LSTM autoencoder availability")
    parser.add_argument("--train-lstm", action="store_true", help="Train the optional LSTM autoencoder")
    args = parser.parse_args(argv)

    if args.lstm_status:
        print(temporal_model_status())
        return

    if args.evaluate:
        print(run_evaluation())
        return

    print("=" * 60)
    print("SKYGUARD AI")
    print("India-Wide Weather Sensor Anomaly Detection")
    print("=" * 60)

    # ========================================================
    # 1. LOAD OBSERVATIONS
    # ========================================================

    print("\n[1/2] Loading observations...")
    df = simulate_observations() if args.simulate else pd.read_csv(args.input)

    print(f"      Dataset shape: {df.shape}")

    if args.train_baseline:
        baseline = train_baseline(df)
        print(f"Baseline trained: {baseline.model_version}")
        return

    if args.train_lstm:
        print(train_lstm_autoencoder(df))
        return

    # ========================================================
    # 2. RUN THE COMPLETE MVP PIPELINE
    # ========================================================

    print("\n[2/2] Running the SkyGuard MVP pipeline...")

    engine_result = SkyGuardEngine().process(df)
    results_df = engine_result.observations
    if args.score_baseline:
        baseline_results = score_with_baseline(df)
        results_df = results_df.merge(
            baseline_results.rename(columns={"Location": "station_id", "DateTime": "timestamp"}),
            on=["station_id", "timestamp"],
            how="left",
        )

    # ========================================================
    # 3. SAVE RESULTS
    # ========================================================

    output_path = resolve_project_path(args.output)

    results_df.to_csv(
        output_path,
        index=False
    )

    # ========================================================
    # 4. SUMMARY
    # ========================================================

    print("\n" + "=" * 60)
    print("PIPELINE COMPLETE")
    print("=" * 60)

    print(f"\nTotal observations: {len(results_df):,}")

    print(
        f"Anomalies detected: "
        f"{results_df['Ensemble_Anomaly'].sum():,}"
    )

    print(
        f"Anomaly percentage: "
        f"{results_df['Ensemble_Anomaly'].mean() * 100:.2f}%"
    )

    print("\nModel agreement:")

    print(
        results_df["Model_Agreement"]
        .value_counts()
        .sort_index()
    )

    print("\nOutput saved to:")
    print(output_path)
    if "ground_truth" in results_df:
        print("\nEvaluation:")
        print(evaluate_detection(results_df))


if __name__ == "__main__":
    main()
