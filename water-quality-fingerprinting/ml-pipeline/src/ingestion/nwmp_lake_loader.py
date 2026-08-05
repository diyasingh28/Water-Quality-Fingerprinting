"""
Loader for the combined CPCB NWMP Lake Monitoring dataset (2017-2022),
built by normalizing station names and stacking each year's official
CPCB lake water quality CSV.

Unlike a typical sensor feed, each row here is a whole YEAR's Min/Max
summary for one lake — not an individual timestamped reading. This loader:
    1. Renames raw CPCB headers to canonical min/max columns
       (see parameter_config.RAW_COLUMN_MAP)
    2. Computes a representative midpoint value per parameter
       (used as the "reading" by the existing single-value pipeline logic)
    3. Computes the range (max - min) per parameter — this is a genuine,
       meaningful fingerprint signal: a lake with a wide BOD swing across
       the year suggests intermittent pollution events (e.g. monsoon
       runoff or periodic industrial discharge), not a data artifact.
"""

import pandas as pd
from pathlib import Path

from .base_source import BaseWaterQualitySource
from ..utils.parameter_config import AVAILABLE_PARAMETERS, RAW_COLUMN_MAP


class NWMPLakeSource(BaseWaterQualitySource):
    # Override — this dataset has its own real, verified column set,
    # not the original 10-parameter placeholder assumption.
    REQUIRED_COLUMNS = ["station_id", "year"] + [
        f"{p}_min" for p in AVAILABLE_PARAMETERS
    ] + [f"{p}_max" for p in AVAILABLE_PARAMETERS]

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)

    def fetch(self) -> pd.DataFrame:
        if not self.filepath.exists():
            raise FileNotFoundError(
                f"Combined NWMP lake dataset not found at {self.filepath}. "
                "Run the year-combining step first (see docs/phase1_report.md)."
            )
        df = pd.read_csv(self.filepath)
        df = df.rename(columns=RAW_COLUMN_MAP)

        # station_id, State Name, Type Water Body, year already normalized
        # when the 6 years were combined — no further renaming needed there.

        for param in AVAILABLE_PARAMETERS:
            min_col, max_col = f"{param}_min", f"{param}_max"
            if min_col not in df.columns or max_col not in df.columns:
                continue
            df[min_col] = pd.to_numeric(df[min_col], errors="coerce")
            df[max_col] = pd.to_numeric(df[max_col], errors="coerce")

            # Midpoint = representative single value for this station-year,
            # used by the existing single-value fingerprint/model logic.
            df[param] = (df[min_col] + df[max_col]) / 2

            # Range = variability signal within the year — a real,
            # additional fingerprint feature, not filler.
            df[f"{param}_range"] = df[max_col] - df[min_col]

        # Drop raw text columns now redundant with station_id — these are
        # NOT numeric features and would otherwise leak into the model as
        # unparseable strings ("ASHAIBAGH BRIDGE" etc.) and crash training.
        df = df.drop(
            columns=["Name of Monitoring Location", "STN Code"],
            errors="ignore",
        )

        return self.validate(df)
