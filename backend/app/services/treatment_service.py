"""Maps predicted pollution categories (and their top SHAP drivers, actual
sample values, and typical category ranges) to suggested treatment/
remediation approaches. Mappings are based on standard water-treatment
literature, not verified site-specific engineering advice -- intended as a
starting-point decision aid, not a substitute for expert assessment.
"""

CATEGORY_TREATMENTS = {
    "sewage_domestic": [
        "Constructed wetlands for biological treatment of organic load",
        "Activated sludge treatment to reduce BOD and pathogens",
        "Disinfection (chlorination or UV) to eliminate coliform bacteria",
        "Upgrade/extend sewage interception to prevent untreated discharge",
    ],
    "industrial": [
        "Chemical precipitation to remove dissolved metals/ions",
        "Activated carbon adsorption for organic/chemical contaminants",
        "Membrane filtration (RO/UF) for high dissolved-solid loads",
        "Enforce industrial effluent treatment before discharge (ETP compliance)",
    ],
    "agricultural_runoff": [
        "Vegetative buffer strips along field boundaries to filter runoff",
        "Constructed wetlands to absorb excess nutrients (nitrate)",
        "Controlled/optimized fertilizer application (nutrient management)",
        "Drainage water management to reduce peak runoff nitrate loading",
    ],
    "natural_background": [
        "No active treatment required -- continue routine monitoring",
        "Maintain riparian vegetation to preserve natural water quality",
    ],
    "unclassified": [
        "Insufficient signal for a specific recommendation -- recommend "
        "additional sampling or manual expert review before acting",
    ],
}

# Feature -> (unit, targeted action). Used to build a value-specific
# sentence rather than a generic one.
FEATURE_TREATMENT_ACTIONS = {
    "bod": ("mg/L", "aeration or oxidation ponds to reduce organic load"),
    "fecal_coliform": ("MPN/100ml", "disinfection (chlorination or UV treatment)"),
    "total_coliform": ("MPN/100ml", "an added disinfection step in the treatment plan"),
    "conductivity": ("\u00b5mhos/cm", "membrane filtration or ion exchange"),
    "nitrate": ("mg/L", "denitrification or constructed wetlands"),
    "dissolved_oxygen": ("mg/L", "aeration to restore oxygen levels"),
}

# dissolved_oxygen is inverted -- LOW values are the problem, not high.
INVERTED_PARAMS = {"dissolved_oxygen"}


def _base_feature_name(feature: str) -> str:
    for suffix in ["_rollmean", "_rollstd", "_range", "_min", "_max"]:
        if feature.endswith(suffix):
            return feature[: -len(suffix)]
    return feature


def _severity_for_value(param: str, value: float, category_range: dict) -> str:
    """Compares the actual value against this category's typical range and
    returns a plain-language severity label."""
    if not category_range or value is None:
        return "elevated"

    typical_high = category_range.get("typical_high")
    typical_low = category_range.get("typical_low")
    if typical_high is None or typical_low is None:
        return "elevated"

    if param in INVERTED_PARAMS:
        # Lower is worse for DO -- flip the comparison.
        if value <= typical_low:
            return "well below"
        return "within"

    span = typical_high - typical_low
    if span <= 0:
        return "elevated"

    if value >= typical_high + span:
        return "severely elevated (well above"
    if value >= typical_high:
        return "elevated (above"
    return "within"


def get_recommendations(
    predicted_class: str,
    top_features: list,
    sample_values: dict | None = None,
    category_ranges: dict | None = None,
    station_name: str | None = None,
) -> dict:
    general = CATEGORY_TREATMENTS.get(
        predicted_class, CATEGORY_TREATMENTS["unclassified"]
    )

    this_category_ranges = (category_ranges or {}).get(predicted_class, {})

    targeted = []
    seen_bases = set()
    for f in top_features:
        if f.get("shap_value", 0) <= 0:
            continue  # only features that pushed toward the predicted class
        base = _base_feature_name(f["feature"])
        if base in seen_bases or base not in FEATURE_TREATMENT_ACTIONS:
            continue

        unit, action = FEATURE_TREATMENT_ACTIONS[base]
        value = (sample_values or {}).get(base)
        param_range = this_category_ranges.get(base)

        if value is not None and param_range:
            severity = _severity_for_value(base, value, param_range)
            range_text = f"{param_range['typical_low']}\u2013{param_range['typical_high']} {unit}"
            label = base.replace("_", " ").title()
            tip = (
                f"{label} measured at {value} {unit} is {severity} "
                f"the typical {predicted_class.replace('_', ' ')} range "
                f"({range_text}) -- prioritize {action}."
            )
        else:
            label = base.replace("_", " ").title()
            tip = f"Elevated {label} suggests prioritizing {action}."

        targeted.append(tip)
        seen_bases.add(base)
        if len(targeted) >= 3:
            break

    result = {
        "predicted_class": predicted_class,
        "general_recommendations": general,
        "targeted_recommendations": targeted,
    }
    if station_name:
        result["station_name"] = station_name
    return result