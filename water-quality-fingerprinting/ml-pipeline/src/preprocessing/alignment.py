"""Align readings by station and time window (useful once multiple sources merge)."""

import pandas as pd


def align_by_station_time(df: pd.DataFrame, freq: str = "D") -> pd.DataFrame:
    """
    Resample/aggregate readings per station to a consistent time frequency
    (default: daily). Prevents duplicate/irregular timestamps from skewing
    fingerprint features.
    """
    df = df.copy()
    df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
    df = df.dropna(subset=["timestamp", "station_id"])

    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    grouped = (
        df.set_index("timestamp")
        .groupby("station_id")[numeric_cols]
        .resample(freq)
        .mean()
        .reset_index()
    )
    return grouped


def merge_sources(*dfs: pd.DataFrame) -> pd.DataFrame:
    """Concatenate multiple source DataFrames (e.g. CPCB + TNPCB) into one."""
    return pd.concat(dfs, ignore_index=True).drop_duplicates(
        subset=["station_id", "timestamp"]
    )


def align_by_station_year(df: pd.DataFrame) -> pd.DataFrame:
    """
    For datasets that are already one row per station per year (like the
    combined NWMP lake dataset) — no daily resampling needed. Just sorts
    chronologically per station and drops exact station-year duplicates,
    so rolling/trend features compute in the correct order.
    """
    df = df.copy()
    df = df.dropna(subset=["station_id", "year"])
    df = df.drop_duplicates(subset=["station_id", "year"], keep="last")
    df = df.sort_values(["station_id", "year"]).reset_index(drop=True)
    return df
