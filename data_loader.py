import pandas as pd

def load_telemetry(path="telemetry_data.xlsx"):
    df = pd.read_excel(path, engine="openpyxl")

    df.columns = [c.strip() for c in df.columns]

    # --- FIX: Use TimeStamp only ---
    if "TimeStamp" in df.columns:
        df["datetime"] = pd.to_datetime(
            df["TimeStamp"],
            format="%Y-%m-%d_%H-%M-%S.%f",
            errors="coerce"
        )
    else:
        df["datetime"] = pd.RangeIndex(len(df))  # fallback

    # Fill missing important columns
    needed = [
        "PlatformRoll", "PlatformPitch", "PlatformHeading",
        "SensorTrueAltitude", "SensorLatitude", "SensorLongitude"
    ]

    for col in needed:
        if col not in df.columns:
            df[col] = 0

    df = df.sort_values("datetime").reset_index(drop=True)

    df[needed] = df[needed].ffill().fillna(0)

    return df
