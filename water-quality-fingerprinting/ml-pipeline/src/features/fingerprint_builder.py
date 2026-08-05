"""
Builds the "fingerprint" feature vector per water sample/station — this is
the core novelty of the project: turning raw parameter readings into a
signature that XGBoost/RF can classify by likely pollution source, and that
SHAP can explain.
"""

import numpy as np
import pandas as pd

from .feature_config import POLLUTION_SOURCE_RULES, FINGERPRINT_RATIOS


def add_ratio_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add engineered ratio features between key parameter pairs."""
    df = df.copy()
    for num, den in FINGERPRINT_RATIOS:
        if num in df.columns and den in df.columns:
            col_name = f"{num}_to_{den}_ratio"
            df[col_name] = df[num] / df[den].replace(0, np.nan)
            df[col_name] = df[col_name].fillna(0)
    return df


def add_statistical_features(df: pd.DataFrame, window: int = 3, time_col: str = "year") -> pd.DataFrame:
    """
    Rolling statistics per station — captures multi-year trend/variability,
    which is often a stronger pollution-source signal than a single
    snapshot. Defaults to grouping by year (matches the NWMP lake dataset,
    which is one row per station per year); pass time_col="timestamp" for
    a future dataset with individual timestamped readings instead.
    """
    df = df.copy().sort_values(["station_id", time_col])
    exclude = {time_col, "station_id"}
    numeric_cols = [
        c for c in df.select_dtypes(include="number").columns if c not in exclude
    ]

    for col in numeric_cols:
        df[f"{col}_rollmean"] = (
            df.groupby("station_id")[col]
            .transform(lambda s: s.rolling(window, min_periods=1).mean())
        )
        df[f"{col}_rollstd"] = (
            df.groupby("station_id")[col]
            .transform(lambda s: s.rolling(window, min_periods=1).std())
            .fillna(0)
        )
    return df


def rule_based_label(row: pd.Series) -> str:
    """
    Heuristic labeling used ONLY to bootstrap a training set when the raw
    dataset has no ground-truth pollution-source label. Once you have
    domain-expert-verified labels, replace this with the real label column.
    """
    rules = POLLUTION_SOURCE_RULES

    def matches(source_name: str) -> bool:
        cond = rules[source_name]
        for key, threshold in cond.items():
            param = key.rsplit("_", 1)[0]
            if param not in row or pd.isna(row[param]):
                return False
            if key.endswith("_min") and row[param] < threshold:
                return False
            if key.endswith("_max") and row[param] > threshold:
                return False
        return True

    for source in rules:
        if matches(source):
            return source
    return "unclassified"


def build_fingerprint_vectors(df: pd.DataFrame, add_labels: bool = True) -> pd.DataFrame:
    """End-to-end fingerprint feature vector construction."""
    df = add_ratio_features(df)
    df = add_statistical_features(df)

    if add_labels and "pollution_source" not in df.columns:
        df["pollution_source"] = df.apply(rule_based_label, axis=1)

    return df
