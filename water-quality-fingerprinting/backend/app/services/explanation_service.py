"""Wraps the SHAP explainer for use in the /explain API endpoint."""

import joblib
from pathlib import Path
from functools import lru_cache

from app.core.config import settings

# Human-friendly base descriptions -- kept in sync with the 8 real
# available parameters (app/core/parameters.py).
FEATURE_DESCRIPTIONS = {
    "ph": "pH level",
    "dissolved_oxygen": "Dissolved Oxygen level",
    "bod": "Biochemical Oxygen Demand",
    "conductivity": "Electrical Conductivity",
    "nitrate": "Nitrate + Nitrite concentration",
    "fecal_coliform": "Fecal Coliform count",
    "total_coliform": "Total Coliform count",
    "temperature": "Temperature",
}

RATIO_DESCRIPTIONS = {
    "bod_to_dissolved_oxygen_ratio": "BOD-to-Dissolved-Oxygen ratio (oxygen demand pressure)",
    "nitrate_to_bod_ratio": "Nitrate-to-BOD ratio (agricultural vs organic indicator)",
    "fecal_coliform_to_bod_ratio": "Fecal-Coliform-to-BOD ratio (biological vs chemical loading)",
    "conductivity_to_bod_ratio": "Conductivity-to-BOD ratio (industrial vs organic loading)",
    "total_coliform_to_fecal_coliform_ratio": "Total-to-Fecal-Coliform ratio (general vs fecal-specific contamination)",
}

# Suffix -> human-readable qualifier. Order matters: check longer/more
# specific suffixes before shorter ones so e.g. "_rollstd" isn't
# accidentally matched by a shorter suffix first.
SUFFIX_QUALIFIERS = [
    ("_rollmean", " (multi-year rolling average)"),
    ("_rollstd", " (multi-year variability)"),
    ("_range", " (within-year Min-Max range)"),
    ("_min", " (yearly minimum)"),
    ("_max", " (yearly maximum)"),
]


def describe_feature(feature_name: str) -> str:
    """
    Best-effort human description for a (possibly engineered) feature name.
    Fixed to preserve which variant (raw / min / max / range / rolling) a
    feature is, instead of collapsing them all into one duplicate label.
    """
    base = feature_name
    qualifier = ""
    for suffix, label in SUFFIX_QUALIFIERS:
        if base.endswith(suffix):
            base = base[: -len(suffix)]
            qualifier = label
            break

    if base in RATIO_DESCRIPTIONS:
        return RATIO_DESCRIPTIONS[base] + qualifier
    if base in FEATURE_DESCRIPTIONS:
        return FEATURE_DESCRIPTIONS[base] + qualifier
    return feature_name.replace("_", " ")


class ExplanationService:
    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        self.explainer = None
        self._load()

    def _load(self):
        try:
            self.explainer = joblib.load(self.model_dir / "shap_explainer.pkl")
        except FileNotFoundError:
            self.explainer = None

    def is_ready(self) -> bool:
        return self.explainer is not None

    def explain(self, X_row, predicted_class: str, top_n: int = 5):
        if not self.is_ready():
            raise RuntimeError(
                "SHAP explainer not found. Run the ML pipeline and copy "
                "shap_explainer.pkl into backend/ml_artifacts/"
            )
        shap_values = self.explainer.shap_values(X_row)
        values = shap_values[0] if isinstance(shap_values, list) else shap_values
        pairs = list(zip(X_row.columns, values.flatten()))
        pairs.sort(key=lambda x: abs(x[1]), reverse=True)
        top = pairs[:top_n]

        top_features = [
            {"feature": f, "shap_value": float(v), "description": describe_feature(f)}
            for f, v in top
        ]
        driver_text = ", ".join(
            f"{'elevated' if v > 0 else 'reduced'} {describe_feature(f)}" for f, v in top
        )
        narrative = f"Predicted source: {predicted_class}. Main drivers: {driver_text}."
        return narrative, top_features


@lru_cache
def get_explanation_service() -> ExplanationService:
    return ExplanationService(settings.model_dir_path)
