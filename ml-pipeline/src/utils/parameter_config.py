"""
SINGLE SOURCE OF TRUTH for which water quality parameters this project
actually has real data for.

This file exists so that adding/removing a parameter later (e.g. Phase 2
sensors adding turbidity, or a new dataset adding COD) only requires an
edit HERE — every other module (cleaning, feature engineering, rules,
backend inference) reads from this list instead of hardcoding its own.

Based on the CPCB NWMP Lake Monitoring dataset (2017-2022), which reports
each parameter as a Min/Max range per station per year (not individual
timestamped readings).
"""

# Canonical parameter names used throughout the whole codebase.
# NOTE: COD, TDS, and turbidity are NOT in this dataset — CPCB's NWMP lake
# program does not measure them. If you later get a dataset/sensor that
# does include them, add the canonical name here and update RAW_COLUMN_MAP
# below; nothing else needs to change structurally.
AVAILABLE_PARAMETERS = [
    "ph",
    "dissolved_oxygen",
    "bod",
    "conductivity",
    "nitrate",
    "fecal_coliform",
    "total_coliform",
    "temperature",
]

# Maps this dataset's actual raw CSV headers (after our name-normalization
# script combined the 6 years) to canonical_min / canonical_max pairs.
RAW_COLUMN_MAP = {
    "Min Temperature": "temperature_min",
    "Max Temperature": "temperature_max",
    "Min Dissolved Oxygen": "dissolved_oxygen_min",
    "Max Dissolved Oxygen": "dissolved_oxygen_max",
    "Min pH": "ph_min",
    "Max pH": "ph_max",
    "Min Conductivity": "conductivity_min",
    "Max Conductivity": "conductivity_max",
    "Min BOD": "bod_min",
    "Max BOD": "bod_max",
    "Min Nitrate N + Nitrite N": "nitrate_min",
    "Max Nitrate N + Nitrite N": "nitrate_max",
    "Min Fecal Coliform": "fecal_coliform_min",
    "Max Fecal Coliform": "fecal_coliform_max",
    "Min Total Coliform": "total_coliform_min",
    "Max Total Coliform": "total_coliform_max",
}

# Non-parameter metadata columns carried through from the raw dataset.
META_COLUMNS = ["station_id", "State Name", "Type Water Body", "year"]
