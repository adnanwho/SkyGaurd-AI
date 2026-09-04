import os
import pandas as pd

from src.anomaly_detection import run_anomaly_pipeline


def main():

    print("=" * 60)
    print("SKYGUARD AI")
    print("India-Wide Weather Sensor Anomaly Detection")
    print("=" * 60)

    # ========================================================
    # 1. LOAD CONSOLIDATED FEATURE DATA
    # ========================================================

    feature_path = "data/processed/SkyGuard_features.csv"

    print("\n[1/2] Loading consolidated feature dataset...")

    df = pd.read_csv(feature_path)

    df["DateTime"] = pd.to_datetime(df["DateTime"])

    print(f"      Dataset shape: {df.shape}")

    # ========================================================
    # 2. RUN ANOMALY DETECTION
    # ========================================================

    print("\n[2/2] Running India-wide anomaly detection...")

    os.makedirs("models", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    results_df = run_anomaly_pipeline(
        df,
        contamination=0.02
    )

    # ========================================================
    # 3. SAVE RESULTS
    # ========================================================

    output_path = "outputs/anomaly_detection_results.csv"

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


if __name__ == "__main__":
    main()