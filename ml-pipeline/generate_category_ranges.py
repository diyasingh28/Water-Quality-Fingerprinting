import pandas as pd
import json
import sys
sys.path.append("src")
from features.feature_config import POLLUTION_SOURCE_RULES

df = pd.read_csv("data/fingerprints/fingerprint_vectors.csv")

BASE_PARAMS = ["ph", "dissolved_oxygen", "bod", "conductivity",
               "nitrate", "fecal_coliform", "total_coliform", "temperature"]

categories = df["pollution_source"].unique().tolist()
ranges = {}

for category in categories:
    subset = df[df["pollution_source"] == category]
    ranges[category] = {}
    for param in BASE_PARAMS:
        if param in subset.columns:
            values = subset[param].dropna()
            if len(values) > 0:
                ranges[category][param] = {
                    "typical_low": round(float(values.quantile(0.25)), 2),
                    "typical_high": round(float(values.quantile(0.75)), 2),
                    "observed_min": round(float(values.min()), 2),
                    "observed_max": round(float(values.max()), 2),
                }

ranges["_rule_thresholds"] = POLLUTION_SOURCE_RULES

with open("data/category_ranges.json", "w") as f:
    json.dump(ranges, f, indent=2)

print("Saved category_ranges.json for categories:", categories)