"""
Domain configuration for fingerprint feature engineering.

Reworked to use ONLY the parameters actually present in the CPCB NWMP lake
dataset: ph, dissolved_oxygen, bod, conductivity, nitrate, fecal_coliform,
total_coliform, temperature. COD, TDS, and turbidity are NOT available in
this dataset and have been removed from the rules below (see
parameter_config.py for the single source of truth on available params).

Thresholds are based on CPCB's general water quality standards / commonly
cited pollution-indicator ranges in Indian water quality literature. These
are starting points -- refine and cite properly once you do a literature
review for the paper; treat these as reasonable defaults, not verified
scientific thresholds.
"""

# Rough indicative pollution-source labels used to bootstrap a training set
# when the raw dataset has no explicit ground-truth label column. Applied
# to the MIDPOINT value of each parameter (see nwmp_lake_loader.py).
POLLUTION_SOURCE_RULES = {
    "sewage_domestic": {
        # High BOD + high coliform counts + low DO is the classic sewage
        # signature (organic/biological loading from untreated sewage).
        "bod_min": 6,
        "fecal_coliform_min": 500,
        "dissolved_oxygen_max": 4,
    },
    "industrial": {
        # High conductivity (dissolved ionic/chemical load) + low
        # biological activity (low fecal coliform) is a rough proxy for
        # industrial/chemical effluent, since we don't have COD/TDS here
        # to confirm it more directly.
        "conductivity_min": 1000,
        "fecal_coliform_max": 500,
        "bod_min": 3,
    },
    "agricultural_runoff": {
        # High nitrate (fertilizer runoff) with only moderate BOD
        # distinguishes this from raw sewage.
        "nitrate_min": 5,
        "bod_max": 6,
    },
    "natural_background": {
        # Falls within CPCB's general "acceptable" limits on all major
        # organic/biological indicators.
        "bod_max": 3,
        "fecal_coliform_max": 500,
        "nitrate_max": 3,
        "dissolved_oxygen_min": 4,
    },
}

# Parameter pairs used to build fingerprint ratio features -- computed on
# the midpoint value of each parameter. Ratios often carry more
# discriminative signal than raw values alone.
FINGERPRINT_RATIOS = [
    ("bod", "dissolved_oxygen"),            # oxygen demand pressure
    ("nitrate", "bod"),                     # agricultural vs organic pollution
    ("fecal_coliform", "bod"),              # biological vs chemical loading
    ("conductivity", "bod"),                # industrial/ionic vs organic loading
    ("total_coliform", "fecal_coliform"),   # general vs fecal-specific contamination
]
