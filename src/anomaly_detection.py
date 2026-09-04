import pandas as pd
import numpy as np
import joblib

from sklearn.ensemble import IsolationForest
from sklearn.preprocessing import StandardScaler

from pyod.models.ecod import ECOD
from pyod.models.copod import COPOD
from pyod.models.hbos import HBOS


# ============================================================
# FINAL MODEL FEATURES
# ============================================================

MODEL_FEATURES = [
    "Temperature_C",
    "Humidity_Percent",
    "Pressure_hPa",

    "Temperature_Diff",
    "Humidity_Diff",
    "Pressure_Diff",

    "Temperature_Deviation",
    "Humidity_Deviation",
    "Pressure_Deviation",

    "Temperature_LocalZ",
    "Humidity_LocalZ",
    "Pressure_LocalZ",

    "Pressure_Missing"
]


# ============================================================
# SCORE NORMALIZATION
# ============================================================

def normalize_scores(scores):
    """
    Convert anomaly scores to the range 0-1.

    Higher value = more anomalous.
    """

    scores = np.asarray(scores)

    min_score = np.min(scores)
    max_score = np.max(scores)

    if max_score - min_score < 1e-12:
        return np.zeros_like(scores)

    return (scores - min_score) / (
        max_score - min_score
    )


# ============================================================
# MAIN ANOMALY DETECTION PIPELINE
# ============================================================

def run_anomaly_pipeline(
    df,
    contamination=0.02
):

    df = df.copy()

    # --------------------------------------------------------
    # Make sure data is sorted
    # --------------------------------------------------------

    df = df.sort_values(
        ["DateTime", "Location"]
    ).reset_index(drop=True)

    # --------------------------------------------------------
    # Prepare model input
    # --------------------------------------------------------
    #
    # IMPORTANT:
    # This is ONE UNIVERSAL MODEL.
    #
    # Location is NOT included in X.
    # --------------------------------------------------------

    X = df[MODEL_FEATURES].copy()

    # --------------------------------------------------------
    # Scaling
    # --------------------------------------------------------

    scaler = StandardScaler()

    X_scaled = scaler.fit_transform(X)

    # ========================================================
    # 1. ISOLATION FOREST
    # ========================================================

    iforest = IsolationForest(
        n_estimators=300,
        contamination=contamination,
        random_state=42,
        n_jobs=-1
    )

    iforest.fit(X_scaled)

    df["IF_Anomaly"] = (
        iforest.predict(X_scaled) == -1
    ).astype(int)

    # Higher = more anomalous
    df["IF_Score_Raw"] = (
        -iforest.decision_function(X_scaled)
    )

    df["IF_Score"] = normalize_scores(
        df["IF_Score_Raw"]
    )

    # ========================================================
    # 2. ECOD
    # ========================================================

    ecod = ECOD(
        contamination=contamination
    )

    ecod.fit(X_scaled)

    df["ECOD_Anomaly"] = (
        ecod.labels_
    )

    df["ECOD_Score"] = normalize_scores(
        ecod.decision_scores_
    )

    # ========================================================
    # 3. COPOD
    # ========================================================

    copod = COPOD(
        contamination=contamination
    )

    copod.fit(X_scaled)

    df["COPOD_Anomaly"] = (
        copod.labels_
    )

    df["COPOD_Score"] = normalize_scores(
        copod.decision_scores_
    )

    # ========================================================
    # 4. HBOS
    # ========================================================

    hbos = HBOS(
        contamination=contamination
    )

    hbos.fit(X_scaled)

    df["HBOS_Anomaly"] = (
        hbos.labels_
    )

    df["HBOS_Score"] = normalize_scores(
        hbos.decision_scores_
    )

    # ========================================================
    # 5. MODEL AGREEMENT
    # ========================================================

    df["Model_Agreement"] = (
        df["IF_Anomaly"]
        + df["ECOD_Anomaly"]
        + df["COPOD_Anomaly"]
        + df["HBOS_Anomaly"]
    )

    # ========================================================
    # 6. ENSEMBLE ANOMALY SCORE
    # ========================================================
    #
    # Average of normalized anomaly scores.
    #
    # 0 = normal
    # 1 = highly anomalous relative to this dataset
    # ========================================================

    df["Ensemble_Score"] = (
        df["IF_Score"]
        + df["ECOD_Score"]
        + df["COPOD_Score"]
        + df["HBOS_Score"]
    ) / 4

    # ========================================================
    # 7. ENSEMBLE DECISION
    # ========================================================
    #
    # Primary high-confidence rule:
    # at least 3 of 4 models must agree.
    #
    # This is a candidate anomaly, NOT ground truth.
    # ========================================================

    df["Ensemble_Anomaly"] = (
        df["Model_Agreement"] >= 3
    ).astype(int)

    # ========================================================
    # 8. ANOMALY SEVERITY
    # ========================================================

    df["Anomaly_Severity"] = pd.cut(
        df["Ensemble_Score"],
        bins=[
            -np.inf,
            0.50,
            0.70,
            0.85,
            np.inf
        ],
        labels=[
            "Normal",
            "Low",
            "Medium",
            "High"
        ]
    )

    # ========================================================
    # 9. SAVE TRAINED COMPONENTS
    # ========================================================

    joblib.dump(
        scaler,
        "models/scaler.pkl"
    )

    joblib.dump(
        iforest,
        "models/isolation_forest.pkl"
    )

    joblib.dump(
        ecod,
        "models/ecod.pkl"
    )

    joblib.dump(
        copod,
        "models/copod.pkl"
    )

    joblib.dump(
        hbos,
        "models/hbos.pkl"
    )

    # ========================================================
    # 10. FINAL SORT
    # ========================================================

    df = df.sort_values(
        ["DateTime", "Location"]
    ).reset_index(drop=True)

    return df