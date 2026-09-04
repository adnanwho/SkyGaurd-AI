import pandas as pd


def load_and_preprocess_raw_data(city_files):

    datasets = []

    for file_path in city_files:

        # ----------------------------------------------------
        # Load raw CSV
        # ----------------------------------------------------
        df = pd.read_csv(file_path)

        # Convert timestamp
        df["DateTime"] = pd.to_datetime(df["Time"])

        # ----------------------------------------------------
        # Resample to 3-hour intervals
        # ----------------------------------------------------
        df = df.set_index("DateTime")

        df_3h = df.resample("3h").agg({
            "Location": "first",
            "Temperature_C": "first",
            "Humidity_Percent": "first",
            "Pressure_hPa": "first"
        }).reset_index()

        # ----------------------------------------------------
        # Remove completely empty observations
        # ----------------------------------------------------
        df_3h = df_3h.dropna(
            subset=[
                "Temperature_C",
                "Humidity_Percent",
                "Pressure_hPa"
            ],
            how="all"
        ).reset_index(drop=True)

        # ----------------------------------------------------
        # Track missing pressure readings
        # BEFORE interpolation
        # ----------------------------------------------------
        df_3h["Pressure_Missing"] = (
            df_3h["Pressure_hPa"].isna().astype(int)
        )

        # ----------------------------------------------------
        # Interpolate pressure
        # ----------------------------------------------------
        df_3h = df_3h.set_index("DateTime")

        df_3h["Pressure_hPa"] = (
            df_3h["Pressure_hPa"]
            .interpolate(
                method="time",
                limit_direction="both"
            )
        )

        df_3h = df_3h.reset_index()

        # ----------------------------------------------------
        # Remove remaining missing sensor values
        # ----------------------------------------------------
        df_3h = df_3h.dropna(
            subset=[
                "Temperature_C",
                "Humidity_Percent",
                "Pressure_hPa"
            ]
        ).reset_index(drop=True)

        datasets.append(df_3h)

    # --------------------------------------------------------
    # Combine all stations
    # --------------------------------------------------------
    final_df = pd.concat(
        datasets,
        ignore_index=True
    )

    # --------------------------------------------------------
    # Final ordering
    # --------------------------------------------------------
    final_df = final_df.sort_values(
        ["DateTime", "Location"]
    ).reset_index(drop=True)

    return final_df