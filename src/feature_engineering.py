import pandas as pd
import numpy as np


def create_features(final_df):

    df = final_df.copy()

    # ============================================================
    # 1. SORT DATA
    # ============================================================
    # Location is used only to calculate each station's history.
    # It will NOT be used as a model feature.
    df = df.sort_values(
        ["Location", "DateTime"]
    ).reset_index(drop=True)

    # ============================================================
    # 2. DIFFERENCE FEATURES
    # ============================================================
    grouped = df.groupby("Location")

    df["Temperature_Diff"] = (
        grouped["Temperature_C"].diff()
    )

    df["Humidity_Diff"] = (
        grouped["Humidity_Percent"].diff()
    )

    df["Pressure_Diff"] = (
        grouped["Pressure_hPa"].diff()
    )

    # ============================================================
    # 3. PREVIOUS-OBSERVATION ROLLING STATISTICS
    # ============================================================
    # IMPORTANT:
    # shift(1) prevents the current reading from influencing
    # its own baseline.
    #
    # 4 observations = previous 12 hours because data is 3-hourly.
    # ============================================================

    window = 4

    df["Temperature_RollingMean"] = (
        grouped["Temperature_C"]
        .transform(
            lambda x: x.shift(1).rolling(window).mean()
        )
    )

    df["Humidity_RollingMean"] = (
        grouped["Humidity_Percent"]
        .transform(
            lambda x: x.shift(1).rolling(window).mean()
        )
    )

    df["Pressure_RollingMean"] = (
        grouped["Pressure_hPa"]
        .transform(
            lambda x: x.shift(1).rolling(window).mean()
        )
    )

    df["Temperature_RollingStd"] = (
        grouped["Temperature_C"]
        .transform(
            lambda x: x.shift(1).rolling(window).std()
        )
    )

    df["Humidity_RollingStd"] = (
        grouped["Humidity_Percent"]
        .transform(
            lambda x: x.shift(1).rolling(window).std()
        )
    )

    df["Pressure_RollingStd"] = (
        grouped["Pressure_hPa"]
        .transform(
            lambda x: x.shift(1).rolling(window).std()
        )
    )

    # ============================================================
    # 4. DEVIATION FROM RECENT NORMAL
    # ============================================================

    df["Temperature_Deviation"] = (
        df["Temperature_C"]
        - df["Temperature_RollingMean"]
    )

    df["Humidity_Deviation"] = (
        df["Humidity_Percent"]
        - df["Humidity_RollingMean"]
    )

    df["Pressure_Deviation"] = (
        df["Pressure_hPa"]
        - df["Pressure_RollingMean"]
    )

    # ============================================================
    # 5. LOCAL Z-SCORES
    # ============================================================

    epsilon = 1e-6

    df["Temperature_LocalZ"] = (
        df["Temperature_Deviation"]
        / (df["Temperature_RollingStd"] + epsilon)
    )

    df["Humidity_LocalZ"] = (
        df["Humidity_Deviation"]
        / (df["Humidity_RollingStd"] + epsilon)
    )

    df["Pressure_LocalZ"] = (
        df["Pressure_Deviation"]
        / (df["Pressure_RollingStd"] + epsilon)
    )

    # ============================================================
    # 6. REMOVE INTERNAL ROLLING FEATURES
    # ============================================================
    #
    # Rolling Mean and Rolling Std are only used to calculate
    # Deviation and Local Z.
    #
    # They are NOT directly given to the anomaly models.
    # ============================================================

    df = df.drop(
        columns=[
            "Temperature_RollingMean",
            "Humidity_RollingMean",
            "Pressure_RollingMean",
            "Temperature_RollingStd",
            "Humidity_RollingStd",
            "Pressure_RollingStd"
        ]
    )

    # ============================================================
    # 7. DROP WARM-UP OBSERVATIONS
    # ============================================================
    #
    # First observations don't have enough previous history
    # to calculate the 4-point rolling statistics.
    #
    # DO NOT bfill/ffill these values.
    # ============================================================

    required_features = [
        "Temperature_Diff",
        "Humidity_Diff",
        "Pressure_Diff",
        "Temperature_Deviation",
        "Humidity_Deviation",
        "Pressure_Deviation",
        "Temperature_LocalZ",
        "Humidity_LocalZ",
        "Pressure_LocalZ"
    ]

    df = df.dropna(
        subset=required_features
    ).reset_index(drop=True)

    # ============================================================
    # 8. FINAL MODEL FEATURES
    # ============================================================

    model_features = [
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
    # 9. FINAL SORT
    # ============================================================

    df = df.sort_values(
        ["DateTime", "Location"]
    ).reset_index(drop=True)

    return df