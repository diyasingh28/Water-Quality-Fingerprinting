import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.preprocessing.cleaning import coerce_numeric, impute_missing, remove_outliers_iqr


def sample_df():
    return pd.DataFrame({
        "station_id": ["S1", "S1", "S2"],
        "ph": [7.0, None, 6.8],
        "bod": [3.0, 500.0, 4.0],  # 500 is an outlier
    })


def test_coerce_numeric():
    df = sample_df()
    out = coerce_numeric(df)
    assert out["ph"].dtype.kind in "fc"


def test_impute_missing():
    df = coerce_numeric(sample_df())
    out = impute_missing(df)
    assert out["ph"].isna().sum() == 0


def test_remove_outliers_iqr():
    df = coerce_numeric(sample_df())
    df = impute_missing(df)
    out = remove_outliers_iqr(df)
    assert out["bod"].max() < 500
