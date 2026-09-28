"""Computes a heuristic severity score for a station's latest prediction,
used only to rank urgency in the Action Center -- not a validated
environmental risk metric, just a relative prioritization signal based on
how far key parameters exceed this category's typical range.
"""

KEY_PARAMS_PER_CATEGORY = {
    "sewage_domestic": ["bod", "fecal_coliform", "dissolved_oxygen"],
    "industrial": ["conductivity", "bod"],
    "agricultural_runoff": ["nitrate", "bod"],
}

INVERTED_PARAMS = {"dissolved_oxygen"}  # lower is worse, not higher
ACTIONABLE_CATEGORIES = set(KEY_PARAMS_PER_CATEGORY.keys())


def _midpoint(reading, param: str):
    min_v = getattr(reading, f"{param}_min", None)
    max_v = getattr(reading, f"{param}_max", None)
    if min_v is None or max_v is None:
        return None
    return (min_v + max_v) / 2


def compute_severity(reading, category_ranges: dict) -> dict:
    category = reading.predicted_source

    if category not in ACTIONABLE_CATEGORIES:
        return {"score": 0.0, "label": "None", "actionable": False}

    cat_ranges = (category_ranges or {}).get(category, {})
    worst = 0.0

    for param in KEY_PARAMS_PER_CATEGORY[category]:
        value = _midpoint(reading, param)
        param_range = cat_ranges.get(param)
        if value is None or not param_range:
            continue

        if param in INVERTED_PARAMS:
            typical_low = param_range.get("typical_low")
            if typical_low and typical_low > 0.5 and value < typical_low:  # guard: denominator must be meaningfully non-zero
                worst = max(worst, (typical_low - value) / typical_low * 100)
        else:
            typical_high = param_range.get("typical_high")
            if typical_high and typical_high > 0.5 and value > typical_high:  # same guard
                worst = max(worst, (value - typical_high) / typical_high * 100)

    worst = min(worst, 300)  # cap at 300% -- anything beyond this is noise, not signal

    if worst >= 50:
        label = "Severe"
    elif worst >= 15:
        label = "High"
    elif worst > 0:
        label = "Moderate"
    else:
        label = "Low"

    return {"score": round(worst, 1), "label": label, "actionable": True}