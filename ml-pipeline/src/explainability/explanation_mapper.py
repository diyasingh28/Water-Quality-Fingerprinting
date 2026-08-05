"""Maps raw SHAP feature-importance pairs to human-readable explanations."""

# Human-friendly descriptions for the most common fingerprint features.
# Extend this as you add more engineered features.
FEATURE_DESCRIPTIONS = {
    "bod": "Biochemical Oxygen Demand",
    "cod": "Chemical Oxygen Demand",
    "dissolved_oxygen": "Dissolved Oxygen level",
    "fecal_coliform": "Fecal Coliform count",
    "turbidity": "Turbidity",
    "tds": "Total Dissolved Solids",
    "conductivity": "Electrical Conductivity",
    "nitrate": "Nitrate concentration",
    "ph": "pH level",
    "bod_to_cod_ratio": "BOD-to-COD ratio (biodegradability indicator)",
    "cod_to_dissolved_oxygen_ratio": "Oxygen demand pressure",
    "tds_to_conductivity_ratio": "TDS-to-Conductivity consistency",
    "nitrate_to_bod_ratio": "Nitrate-to-BOD ratio (agricultural vs organic indicator)",
}


def describe_feature(feature_name: str) -> str:
    """Best-effort human description for a (possibly engineered) feature name."""
    base = feature_name.replace("_rollmean", " (rolling average)").replace(
        "_rollstd", " (rolling variability)"
    )
    for key, desc in FEATURE_DESCRIPTIONS.items():
        if base.startswith(key):
            suffix = base[len(key):]
            return desc + suffix
    return feature_name.replace("_", " ")


def build_explanation_narrative(predicted_class: str, shap_pairs, top_n: int = 5) -> str:
    """
    Turns SHAP top features into a short narrative suitable for the
    dashboard, e.g.:
    "Predicted source: Industrial. Main drivers: elevated Electrical
    Conductivity, elevated Total Dissolved Solids, ..."
    """
    top_features = shap_pairs[:top_n]
    driver_phrases = []
    for feature, value in top_features:
        direction = "elevated" if value > 0 else "reduced"
        driver_phrases.append(f"{direction} {describe_feature(feature)}")

    drivers_text = ", ".join(driver_phrases)
    return f"Predicted source: {predicted_class}. Main drivers: {drivers_text}."
