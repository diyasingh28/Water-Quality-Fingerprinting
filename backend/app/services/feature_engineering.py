"""
Rebuilds the exact same fingerprint features used at training time
(ml-pipeline/src/features/fingerprint_builder.py), so backend predictions
are computed consistently with what the model actually learned.

Given the current sample + a station's stored history (from the DB), this
computes: midpoint, range, ratio features, and rolling mean/std across
years -- in the same way the training pipeline does.
"""

import pandas as pd
import numpy as np

from app.core.parameters import AVAILABLE_PARAMETERS, FINGERPRINT_RATIOS, ROLLING_WINDOW


def _row_to_midpoint_and_range(row: dict) -> dict:
    """Given {param}_min / {param}_max, compute the midpoint and range,
    same as nwmp_lake_loader.py does at training time."""
    out = dict(row)
    for p in AVAILABLE_PARAMETERS:
        min_v, max_v = row.get(f"{p}_min"), row.get(f"{p}_max")
        if min_v is None or max_v is None:
            continue
        out[p] = (min_v + max_v) / 2
        out[f"{p}_range"] = max_v - min_v
    return out


def _add_ratio_features(row: dict) -> dict:
    out = dict(row)
    for num, den in FINGERPRINT_RATIOS:
        denom = out.get(den)
        out[f"{num}_to_{den}_ratio"] = (out.get(num, 0) / denom) if denom else 0
    return out


def build_feature_row(current_sample: dict, history_rows: list[dict]) -> pd.DataFrame:
    """
    current_sample: dict with station_id, year, and {param}_min/{param}_max
    history_rows: list of prior stored readings for this same station
                  (each a dict with the same shape), ordered oldest->newest,
                  NOT including current_sample.

    Returns a single-row DataFrame with the full feature set matching
    what the model was trained on (feature_columns.pkl defines the exact
    column order expected).
    """
    all_rows = history_rows + [current_sample]

    processed = [_add_ratio_features(_row_to_midpoint_and_range(r)) for r in all_rows]
    df = pd.DataFrame(processed).sort_values("year").reset_index(drop=True)

    numeric_cols = [
        c for c in df.select_dtypes(include="number").columns
        if c not in ("year",)
    ]
    for col in numeric_cols:
        df[f"{col}_rollmean"] = df[col].rolling(ROLLING_WINDOW, min_periods=1).mean()
        df[f"{col}_rollstd"] = df[col].rolling(ROLLING_WINDOW, min_periods=1).std().fillna(0)

    # Only the last row (the current sample) is the one we want to predict on
    return df.tail(1).reset_index(drop=True)
