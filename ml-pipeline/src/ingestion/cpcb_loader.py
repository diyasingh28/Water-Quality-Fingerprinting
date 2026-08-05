"""
Loader for CPCB (Central Pollution Control Board) public water quality data.

Usage:
    loader = CPCBLoader("data/raw/cpcb_water_quality.csv")
    df = loader.fetch()

Download CPCB data manually from https://cpcb.nic.in/ or https://data.gov.in/
and place the CSV under `ml-pipeline/data/raw/`. Update COLUMN_MAP below to
match whatever column names the actual downloaded file uses — CPCB exports
vary in naming across years/states.
"""

import pandas as pd
from pathlib import Path
from .base_source import BaseWaterQualitySource


class CPCBLoader(BaseWaterQualitySource):
    # Map raw CPCB column names -> canonical column names.
    # EDIT THIS after inspecting your actual downloaded CSV headers.
    COLUMN_MAP = {
        "Station Code": "station_id",
        "Sampling Date": "timestamp",
        "PH": "ph",
        "Dissolved Oxygen (mg/L)": "dissolved_oxygen",
        "BOD (mg/L)": "bod",
        "COD (mg/L)": "cod",
        "Turbidity (NTU)": "turbidity",
        "Total Dissolved Solids (mg/L)": "tds",
        "Conductivity (umhos/cm)": "conductivity",
        "Nitrate N (mg/L)": "nitrate",
        "Fecal Coliform (MPN/100ml)": "fecal_coliform",
        "Temperature (C)": "temperature",
    }

    def __init__(self, filepath: str):
        self.filepath = Path(filepath)

    def fetch(self) -> pd.DataFrame:
        if not self.filepath.exists():
            raise FileNotFoundError(
                f"CPCB dataset not found at {self.filepath}. "
                "Download it from CPCB/data.gov.in and place it in ml-pipeline/data/raw/"
            )
        df = pd.read_csv(self.filepath)
        df = df.rename(columns=self.COLUMN_MAP)
        df["timestamp"] = pd.to_datetime(df["timestamp"], errors="coerce")
        return self.validate(df)
