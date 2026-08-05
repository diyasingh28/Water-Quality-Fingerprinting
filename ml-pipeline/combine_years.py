"""
Combines multiple years of the CPCB NWMP Lake Monitoring CSVs (e.g.
2017_lake_data.csv ... 2022_lake_data.csv) into one normalized dataset,
matching the structure nwmp_lake_loader.py expects.

Usage:
    Place each year's raw CSV in ml-pipeline/data/raw/yearly/
    (e.g. 2017_lake_data.csv, 2018_lake_data.csv, ...)
    Then run:
        python combine_years.py

Output:
    ml-pipeline/data/raw/nwmp_lakes_2017_2022_combined.csv
"""

import re
import sys
from pathlib import Path
import pandas as pd

sys.path.insert(0, str(Path(__file__).parent))
from src.utils.config import RAW_DATA_DIR

YEARLY_DIR = RAW_DATA_DIR / "yearly"
OUTPUT_FILE = RAW_DATA_DIR / "nwmp_lakes_2017_2022_combined.csv"


def normalize_name(name):
    if pd.isna(name):
        return name
    return re.sub(r"\s+", " ", str(name)).strip().upper()


def main():
    if not YEARLY_DIR.exists():
        raise FileNotFoundError(
            f"{YEARLY_DIR} not found. Create it and place each year's raw "
            "CSV inside (e.g. 2017_lake_data.csv, 2018_lake_data.csv, ...)."
        )

    year_files = sorted(YEARLY_DIR.glob("*_lake_data.csv"))
    if not year_files:
        raise FileNotFoundError(f"No *_lake_data.csv files found in {YEARLY_DIR}")

    all_dfs = []
    for f in year_files:
        year_match = re.match(r"(\d{4})", f.stem)
        year = int(year_match.group(1)) if year_match else None

        df = pd.read_csv(f)
        df["State Name"] = df["State Name"].apply(normalize_name)
        df["Name of Monitoring Location"] = df["Name of Monitoring Location"].apply(normalize_name)
        df["Type Water Body"] = df["Type Water Body"].apply(normalize_name)
        df["year"] = year
        all_dfs.append(df)
        print(f"Loaded {f.name}: {len(df)} rows, year={year}")

    combined = pd.concat(all_dfs, ignore_index=True)
    combined["station_id"] = combined["Name of Monitoring Location"]

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    combined.to_csv(OUTPUT_FILE, index=False)

    print(f"\nCombined {len(combined)} rows across {len(year_files)} years.")
    print(f"Saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
