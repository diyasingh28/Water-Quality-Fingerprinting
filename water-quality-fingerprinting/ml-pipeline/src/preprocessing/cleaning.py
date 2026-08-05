"""Missing value handling and outlier detection for water quality data."""

import pandas as pd
import numpy as np

from ..utils.parameter_config import AVAILABLE_PARAMETERS

# NUMERIC_PARAMS now derives from the single source of truth in
# parameter_config.py instead of a separately hardcoded list — keeps this
# module automatically in sync if parameters are added/removed later.
# Includes both the midpoint value (e.g. "bod") AND the within-year range
# (e.g. "bod_range") — both are real, meaningful numeric features for the
# NWMP lake dataset, not just metadata.
NUMERIC_PARAMS = list(AVAILABLE_PARAMETERS) + [f"{p}_range" for p in AVAILABLE_PARAMETERS]


def coerce_numeric(df: pd.DataFrame) -> pd.DataFrame:
    """Force parameter columns to numeric, turning bad values into NaN."""
    df = df.copy()
    for col in NUMERIC_PARAMS:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")
    return df


def impute_missing(df: pd.DataFrame, strategy: str = "station_median") -> pd.DataFrame:
    """
    Fill missing values.
    strategy:
        - "station_median": impute per-station median (falls back to global median)
        - "global_median": impute using the global median for each column
    """
    df = df.copy()
    for col in NUMERIC_PARAMS:
        if col not in df.columns:
            continue
        if strategy == "station_median" and "station_id" in df.columns:
            df[col] = df.groupby("station_id")[col].transform(
                lambda s: s.fillna(s.median())
            )
        df[col] = df[col].fillna(df[col].median())
    return df


def remove_outliers_iqr(df: pd.DataFrame, factor: float = 1.5) -> pd.DataFrame:
    """Clip outliers using the IQR method rather than dropping rows outright."""
    df = df.copy()
    for col in NUMERIC_PARAMS:
        if col not in df.columns:
            continue
        q1, q3 = df[col].quantile(0.25), df[col].quantile(0.75)
        iqr = q3 - q1
        lower, upper = q1 - factor * iqr, q3 + factor * iqr
        df[col] = df[col].clip(lower=lower, upper=upper)
    return df


def clean_pipeline(df: pd.DataFrame) -> pd.DataFrame:
    """Convenience wrapper chaining the standard cleaning steps."""
    df = coerce_numeric(df)
    df = impute_missing(df)
    df = remove_outliers_iqr(df)
    return df
