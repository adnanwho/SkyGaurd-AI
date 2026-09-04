# ============================================================
# SKYGUARD AI — PyOD CLASSICAL MODEL BENCHMARK
# ============================================================

import pandas as pd
import numpy as np
import time

from sklearn.preprocessing import StandardScaler
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    confusion_matrix
)

# PyOD models
from pyod.models.iforest import IForest
from pyod.models.ecod import ECOD
from pyod.models.copod import COPOD
from pyod.models.hbos import HBOS
from pyod.models.knn import KNN
from pyod.models.lof import LOF
from pyod.models.ocsvm import OCSVM
from pyod.models.pca import PCA


# ============================================================
# 1. LOAD DATA
# ============================================================

DATA_PATH = "your_clean_dataset.csv"

df = pd.read_csv(DATA_PATH)

df["Time"] = pd.to_datetime(df["Time"], errors="coerce")

numeric_cols = [
    "Temperature_C",
    "Humidity_Percent",
    "Pressure_hPa"
]

for col in numeric_cols:
    df[col] = pd.to_numeric(df[col], errors="coerce")

df = df.dropna(
    subset=["Location", "Time"]
)

df = df.sort_values(
    ["Location", "Time"]
).reset_index(drop=True)

print("Dataset:", df.shape)
print("Locations:", df["Location"].unique())


# ============================================================
# 2. FEATURE ENGINEERING
# ============================================================

def create_features(data):

    data = data.copy()

    for col in numeric_cols:

        # Change from previous observation
        data[f"{col}_diff"] = (
            data.groupby("Location")[col]
            .diff()
        )

        # Rolling mean
        data[f"{col}_rolling_mean"] = (
            data.groupby("Location")[col]
            .transform(
                lambda x: x.rolling(
                    window=6,
                    min_periods=2
                ).mean()
            )
        )

        # Rolling standard deviation
        data[f"{col}_rolling_std"] = (
            data.groupby("Location")[col]
            .transform(
                lambda x: x.rolling(
                    window=6,
                    min_periods=2
                ).std()
            )
        )

        # Difference from local baseline
        data[f"{col}_deviation"] = (
            data[col]
            - data[f"{col}_rolling_mean"]
        )

    return data


df = create_features(df)


# ============================================================
# 3. FEATURES
# ============================================================

feature_cols = [
    "Temperature_C",
    "Humidity_Percent",
    "Pressure_hPa",

    "Temperature_C_diff",
    "Humidity_Percent_diff",
    "Pressure_hPa_diff",

    "Temperature_C_rolling_mean",
    "Humidity_Percent_rolling_mean",
    "Pressure_hPa_rolling_mean",

    "Temperature_C_rolling_std",
    "Humidity_Percent_rolling_std",
    "Pressure_hPa_rolling_std",

    "Temperature_C_deviation",
    "Humidity_Percent_deviation",
    "Pressure_hPa_deviation"
]

df = df.dropna(
    subset=feature_cols
).reset_index(drop=True)


# ============================================================
# 4. CHRONOLOGICAL TRAIN / TEST SPLIT
# ============================================================

train_parts = []
test_parts = []

TRAIN_RATIO = 0.70

for location, group in df.groupby("Location"):

    group = group.sort_values("Time")

    split = int(
        len(group) * TRAIN_RATIO
    )

    train_parts.append(
        group.iloc[:split]
    )

    test_parts.append(
        group.iloc[split:]
    )


train_df = pd.concat(
    train_parts,
    ignore_index=True
)

test_df = pd.concat(
    test_parts,
    ignore_index=True
)

print("\nTrain:", train_df.shape)
print("Test :", test_df.shape)


# ============================================================
# 5. SCALE DATA
# ============================================================

scaler = StandardScaler()

X_train = scaler.fit_transform(
    train_df[feature_cols]
)

X_test = scaler.transform(
    test_df[feature_cols]
)


# ============================================================
# 6. ANOMALY INJECTION
# ============================================================

def inject_anomalies(data, fraction=0.10):

    data = data.copy()

    data["is_anomaly"] = 0
    data["anomaly_type"] = "normal"

    rng = np.random.default_rng(42)

    n = len(data)

    anomaly_count = int(
        n * fraction
    )

    indices = rng.choice(
        n,
        anomaly_count,
        replace=False
    )

    groups = np.array_split(
        indices,
        6
    )

    # --------------------------------------------------------
    # SPIKE
    # --------------------------------------------------------

    for i in groups[0]:

        data.loc[i, "Temperature_C"] += rng.uniform(
            15, 30
        )

        data.loc[i, "is_anomaly"] = 1
        data.loc[i, "anomaly_type"] = "spike"


    # --------------------------------------------------------
    # DROP
    # --------------------------------------------------------

    for i in groups[1]:

        data.loc[i, "Temperature_C"] -= rng.uniform(
            10, 20
        )

        data.loc[i, "is_anomaly"] = 1
        data.loc[i, "anomaly_type"] = "drop"


    # --------------------------------------------------------
    # HUMIDITY CORRUPTION
    # --------------------------------------------------------

    for i in groups[2]:

        data.loc[i, "Humidity_Percent"] = np.clip(
            data.loc[i, "Humidity_Percent"]
            + rng.uniform(20, 40),
            0,
            100
        )

        data.loc[i, "is_anomaly"] = 1
        data.loc[i, "anomaly_type"] = "humidity_corruption"


    # --------------------------------------------------------
    # PRESSURE SPIKE
    # --------------------------------------------------------

    for i in groups[3]:

        data.loc[i, "Pressure_hPa"] += rng.uniform(
            15, 30
        )

        data.loc[i, "is_anomaly"] = 1
        data.loc[i, "anomaly_type"] = "pressure_spike"


    # --------------------------------------------------------
    # MULTIVARIATE INCONSISTENCY
    # --------------------------------------------------------

    for i in groups[4]:

        data.loc[i, "Temperature_C"] += rng.uniform(
            10, 20
        )

        data.loc[i, "is_anomaly"] = 1
        data.loc[i, "anomaly_type"] = (
            "multivariate_inconsistency"
        )


    # --------------------------------------------------------
    # MISSING VALUE
    # --------------------------------------------------------

    for i in groups[5]:

        parameter = rng.choice(
            numeric_cols
        )

        data.loc[i, parameter] = np.nan

        data.loc[i, "is_anomaly"] = 1
        data.loc[i, "anomaly_type"] = (
            "missing_value"
        )

    return data


test_injected = inject_anomalies(
    test_df,
    fraction=0.10
)


# ============================================================
# 7. CREATE FEATURES AGAIN AFTER INJECTION
# ============================================================

test_features = create_features(
    test_injected
)

X_test_df = test_features[
    feature_cols
].copy()

# Handle NaN / infinity
X_test_df = X_test_df.replace(
    [np.inf, -np.inf],
    np.nan
)

X_test_df = X_test_df.fillna(
    train_df[feature_cols].median()
)

X_test = scaler.transform(
    X_test_df
)

y_test = test_features[
    "is_anomaly"
].values


# ============================================================
# 8. DEFINE PYOD MODELS
# ============================================================

CONTAMINATION = 0.10

models = {

    "Isolation Forest": IForest(
        n_estimators=300,
        contamination=CONTAMINATION,
        random_state=42,
        n_jobs=-1
    ),

    "ECOD": ECOD(
        contamination=CONTAMINATION
    ),

    "COPOD": COPOD(
        contamination=CONTAMINATION
    ),

    "HBOS": HBOS(
        contamination=CONTAMINATION
    ),

    "KNN": KNN(
        contamination=CONTAMINATION,
        n_neighbors=20
    ),

    "LOF": LOF(
        contamination=CONTAMINATION,
        n_neighbors=20
    ),

    "OCSVM": OCSVM(
        contamination=CONTAMINATION
    ),

    "PCA": PCA(
        contamination=CONTAMINATION
    )
}


# ============================================================
# 9. RUN BENCHMARK
# ============================================================

results = []

print("\n")
print("=" * 70)
print("SKYGUARD AI — PyOD BENCHMARK")
print("=" * 70)


for name, model in models.items():

    print(f"\nRunning {name}...")

    # Training
    start_train = time.time()

    model.fit(X_train)

    train_time = (
        time.time()
        - start_train
    )

    # Prediction
    start_predict = time.time()

    y_pred = model.predict(
        X_test
    )

    predict_time = (
        time.time()
        - start_predict
    )

    # PyOD:
    # 0 = normal
    # 1 = anomaly

    precision = precision_score(
        y_test,
        y_pred,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        y_pred,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        y_pred,
        zero_division=0
    )

    tn, fp, fn, tp = confusion_matrix(
        y_test,
        y_pred
    ).ravel()

    fpr = fp / (
        fp + tn
    ) if (fp + tn) > 0 else 0

    results.append({

        "Model": name,

        "Precision": precision,

        "Recall": recall,

        "F1": f1,

        "False_Positive_Rate": fpr,

        "Training_Time_sec": train_time,

        "Inference_Time_sec": predict_time

    })


# ============================================================
# 10. RESULTS TABLE
# ============================================================

results_df = pd.DataFrame(
    results
)

results_df = results_df.sort_values(
    "F1",
    ascending=False
)

print("\n")
print("=" * 70)
print("FINAL RESULTS")
print("=" * 70)

print(
    results_df.to_string(
        index=False
    )
)


# ============================================================
# 11. SAVE RESULTS
# ============================================================

results_df.to_csv(
    "skyguard_pyod_benchmark.csv",
    index=False
)

print(
    "\nSaved → skyguard_pyod_benchmark.csv"
)


# ============================================================
# 12. ANOMALY-TYPE ANALYSIS
# ============================================================

best_model_name = results_df.iloc[0]["Model"]

best_model = models[
    best_model_name
]

best_predictions = best_model.predict(
    X_test
)

analysis_df = test_features[
    [
        "anomaly_type",
        "is_anomaly"
    ]
].copy()

analysis_df["prediction"] = (
    best_predictions
)

print("\n")
print("=" * 70)
print(
    f"BEST MODEL: {best_model_name}"
)
print("=" * 70)

for anomaly_type in analysis_df[
    "anomaly_type"
].unique():

    if anomaly_type == "normal":
        continue

    subset = analysis_df[
        analysis_df["anomaly_type"]
        == anomaly_type
    ]

    detection_rate = (
        subset["prediction"].sum()
        / len(subset)
    )

    print(
        f"{anomaly_type:30s}"
        f" {detection_rate:.2%}"
    )