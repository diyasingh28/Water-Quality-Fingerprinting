"""
SINGLE SOURCE OF TRUTH for available parameters -- backend copy.

This mirrors ml-pipeline/src/utils/parameter_config.py. The two services
are separately deployable (different venvs, no shared import path), so
this is intentionally duplicated rather than imported cross-project --
but both files should be kept in sync manually whenever a parameter is
added or removed. If you add a shared internal package later, this is
the first place to consolidate.
"""

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

# Ratio pairs -- must match ml-pipeline/src/features/feature_config.py exactly,
# since the model was trained on features built with this exact list.
FINGERPRINT_RATIOS = [
    ("bod", "dissolved_oxygen"),
    ("nitrate", "bod"),
    ("fecal_coliform", "bod"),
    ("conductivity", "bod"),
    ("total_coliform", "fecal_coliform"),
]

ROLLING_WINDOW = 3  # must match ml-pipeline's add_statistical_features window
