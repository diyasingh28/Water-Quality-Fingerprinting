"""Unit / scale normalization for water quality parameters."""

import pandas as pd
from sklearn.preprocessing import MinMaxScaler, StandardScaler

from .cleaning import NUMERIC_PARAMS


def scale_features(df: pd.DataFrame, method: str = "standard"):
    """
    Scale numeric parameter columns.
    Returns (scaled_df, fitted_scaler) so the scaler can be reused at
    inference time on new/live data (important for Phase 2).
    """
    df = df.copy()
    cols = [c for c in NUMERIC_PARAMS if c in df.columns]

    scaler = StandardScaler() if method == "standard" else MinMaxScaler()
    df[cols] = scaler.fit_transform(df[cols])
    return df, scaler


def apply_existing_scaler(df: pd.DataFrame, scaler) -> pd.DataFrame:
    """Apply an already-fitted scaler (e.g. loaded from disk) to new data."""
    df = df.copy()
    cols = [c for c in NUMERIC_PARAMS if c in df.columns]
    df[cols] = scaler.transform(df[cols])
    return df
