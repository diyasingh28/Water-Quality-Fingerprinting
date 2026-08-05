"""
Loader for Tamil Nadu Pollution Control Board (TNPCB) public water quality data.

Same pattern as CPCBLoader — swap in TNPCB's actual column headers once you
download the dataset (https://tnpcb.gov.in/ or Tamil Nadu open data portal).
"""

import pandas as pd
from pathlib import Path
from .base_source import BaseWaterQualitySource


class TNPCBLoader(BaseWaterQualitySource):
    COLUMN_MAP = {
        "Monitoring Station": "station_id",
        "Date": "timestamp",
        "pH": "ph",
        "DO (mg/l)": "dissolved_oxygen",
        "BOD (mg/l)": "bod",
        "COD (mg/l)": "cod",
        "Turbidity (NTU)": "turbidity",
        "TDS (mg/l)": "tds",
        "Conductivity (micromhos/cm)": "conductivity",
        "Nitrate (mg/l)": "nitrate",
        "Fecal Coliform (MPN/100ml)": "fecal_coliform",
        "Temperature (C)": "temperature",
    }

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)

    def fetch(self) -> pd.DataFrame:
        if not self.filepath.exists():
            raise FileNotFoundError(
                f"TNPCB dataset not found at {self.filepath}. "
                "Download it and place it in ml-pipeline/data/raw/"
            )
        df = pd.read_csv(self.filepath)
        df = df.rename(columns=self.COLUMN_MAP)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        return self.validate(df)
