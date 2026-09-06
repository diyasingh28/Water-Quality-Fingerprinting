# """Wraps the SHAP explainer for use in the /explain API endpoint."""

# import joblib
# from pathlib import Path
# from functools import lru_cache

# from app.core.config import settings

# # Human-friendly base descriptions -- kept in sync with the 8 real
# # available parameters (app/core/parameters.py).
# FEATURE_DESCRIPTIONS = {
#     "ph": "pH level",
#     "dissolved_oxygen": "Dissolved Oxygen level",
#     "bod": "Biochemical Oxygen Demand",
#     "conductivity": "Electrical Conductivity",
#     "nitrate": "Nitrate + Nitrite concentration",
#     "fecal_coliform": "Fecal Coliform count",
#     "total_coliform": "Total Coliform count",
#     "temperature": "Temperature",
# }

# RATIO_DESCRIPTIONS = {
#     "bod_to_dissolved_oxygen_ratio": "BOD-to-Dissolved-Oxygen ratio (oxygen demand pressure)",
#     "nitrate_to_bod_ratio": "Nitrate-to-BOD ratio (agricultural vs organic indicator)",
#     "fecal_coliform_to_bod_ratio": "Fecal-Coliform-to-BOD ratio (biological vs chemical loading)",
#     "conductivity_to_bod_ratio": "Conductivity-to-BOD ratio (industrial vs organic loading)",
#     "total_coliform_to_fecal_coliform_ratio": "Total-to-Fecal-Coliform ratio (general vs fecal-specific contamination)",
# }

# # Suffix -> human-readable qualifier. Order matters: check longer/more
# # specific suffixes before shorter ones so e.g. "_rollstd" isn't
# # accidentally matched by a shorter suffix first.
# SUFFIX_QUALIFIERS = [
#     ("_rollmean", " (multi-year rolling average)"),
#     ("_rollstd", " (multi-year variability)"),
#     ("_range", " (within-year Min-Max range)"),
#     ("_min", " (yearly minimum)"),
#     ("_max", " (yearly maximum)"),
# ]


# def describe_feature(feature_name: str) -> str:
#     """
#     Best-effort human description for a (possibly engineered) feature name.
#     Fixed to preserve which variant (raw / min / max / range / rolling) a
#     feature is, instead of collapsing them all into one duplicate label.
#     """
#     base = feature_name
#     qualifier = ""
#     for suffix, label in SUFFIX_QUALIFIERS:
#         if base.endswith(suffix):
#             base = base[: -len(suffix)]
#             qualifier = label
#             break

#     if base in RATIO_DESCRIPTIONS:
#         return RATIO_DESCRIPTIONS[base] + qualifier
#     if base in FEATURE_DESCRIPTIONS:
#         return FEATURE_DESCRIPTIONS[base] + qualifier
#     return feature_name.replace("_", " ")


# class ExplanationService:
#     def __init__(self, model_dir: Path):
#         self.model_dir = model_dir
#         self.explainer = None
#         self.label_encoder = None
#         self._load()

#     def _load(self):
#         try:
#             self.explainer = joblib.load(self.model_dir / "shap_explainer.pkl")
#             self.label_encoder = joblib.load(self.model_dir / "label_encoder.pkl")
#         except FileNotFoundError:
#             self.explainer = None
#             self.label_encoder = None

#     def is_ready(self) -> bool:
#         return self.explainer is not None and self.label_encoder is not None

#     def explain(self, X_row, predicted_class: str, top_n: int = 10):
#         """
#         Returns:
#             narrative (str): human-readable summary of the main drivers.
#             top_features (list[dict]): top_n features (+ an "other" bucket)
#                 with their SHAP contribution and description.
#             waterfall (dict): base_value, final_value, predicted_class, and
#                 the same contributions list, shaped for a SHAP waterfall
#                 chart on the frontend.
#         """
#         if not self.is_ready():
#             raise RuntimeError(
#                 "SHAP explainer not found. Run the ML pipeline and copy "
#                 "shap_explainer.pkl and label_encoder.pkl into backend/ml_artifacts/"
#             )

#         # shap_values shape: (n_samples, n_features, n_classes)
#         shap_values = self.explainer.shap_values(X_row)

#         class_names = list(self.label_encoder.classes_)
#         class_idx = class_names.index(predicted_class)

#         base_value = float(self.explainer.expected_value[class_idx])

#         # Pick sample 0, all features, the predicted class's contributions.
#         contributions = shap_values[0, :, class_idx]

#         pairs = list(zip(X_row.columns, contributions))
#         pairs.sort(key=lambda x: abs(x[1]), reverse=True)

#         top = pairs[:top_n]
#         remaining = pairs[top_n:]

#         top_features = [
#             {"feature": f, "shap_value": float(v), "description": describe_feature(f)}
#             for f, v in top
#         ]

#         if remaining:
#             other_sum = sum(float(v) for _, v in remaining)
#             top_features.append({
#                 "feature": f"other_{len(remaining)}_features",
#                 "shap_value": other_sum,
#                 "description": f"Combined effect of {len(remaining)} other features",
#             })

#         final_value = base_value + sum(float(v) for _, v in pairs)

#         driver_text = ", ".join(
#             f"{'elevated' if v > 0 else 'reduced'} {describe_feature(f)}" for f, v in top[:5]
#         )
#         narrative = f"Predicted source: {predicted_class}. Main drivers: {driver_text}."

#         waterfall = {
#             "base_value": base_value,
#             "final_value": final_value,
#             "predicted_class": predicted_class,
#             "contributions": top_features,
#         }

#         return narrative, top_features, waterfall


# @lru_cache
# def get_explanation_service() -> ExplanationService:
#     return ExplanationService(settings.model_dir_path)

"""Wraps the SHAP explainer for use in the /explain API endpoint."""

import json
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

SUFFIX_QUALIFIERS = [
    ("_rollmean", " (multi-year rolling average)"),
    ("_rollstd", " (multi-year variability)"),
    ("_range", " (within-year Min-Max range)"),
    ("_min", " (yearly minimum)"),
    ("_max", " (yearly maximum)"),
]

# The 8 real base parameters, used to pull the current sample's actual
# values out of X_row for the category-range comparison table.
BASE_PARAMS = [
    "ph", "dissolved_oxygen", "bod", "conductivity",
    "nitrate", "fecal_coliform", "total_coliform", "temperature",
]


def describe_feature(feature_name: str) -> str:
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
        self.label_encoder = None
        self.category_ranges = None
        self._load()

    def _load(self):
        try:
            self.explainer = joblib.load(self.model_dir / "shap_explainer.pkl")
            self.label_encoder = joblib.load(self.model_dir / "label_encoder.pkl")
        except FileNotFoundError:
            self.explainer = None
            self.label_encoder = None

        try:
            with open(self.model_dir / "category_ranges.json") as f:
                self.category_ranges = json.load(f)
        except FileNotFoundError:
            self.category_ranges = None

    def is_ready(self) -> bool:
        return self.explainer is not None and self.label_encoder is not None

    def explain(self, X_row, predicted_class: str, top_n: int = 10):
        if not self.is_ready():
            raise RuntimeError(
                "SHAP explainer not found. Run the ML pipeline and copy "
                "shap_explainer.pkl and label_encoder.pkl into backend/ml_artifacts/"
            )

        shap_values = self.explainer.shap_values(X_row)

        class_names = list(self.label_encoder.classes_)
        class_idx = class_names.index(predicted_class)

        base_value = float(self.explainer.expected_value[class_idx])
        contributions = shap_values[0, :, class_idx]

        pairs = list(zip(X_row.columns, contributions))
        pairs.sort(key=lambda x: abs(x[1]), reverse=True)

        top = pairs[:top_n]
        remaining = pairs[top_n:]

        top_features = [
            {"feature": f, "shap_value": float(v), "description": describe_feature(f)}
            for f, v in top
        ]

        if remaining:
            other_sum = sum(float(v) for _, v in remaining)
            top_features.append({
                "feature": f"other_{len(remaining)}_features",
                "shap_value": other_sum,
                "description": f"Combined effect of {len(remaining)} other features",
            })

        final_value = base_value + sum(float(v) for _, v in pairs)

        driver_text = ", ".join(
            f"{'elevated' if v > 0 else 'reduced'} {describe_feature(f)}" for f, v in top[:5]
        )
        narrative = f"Predicted source: {predicted_class}. Main drivers: {driver_text}."

        waterfall = {
            "base_value": base_value,
            "final_value": final_value,
            "predicted_class": predicted_class,
            "contributions": top_features,
        }

        # Current sample's actual values for the 8 base parameters, so the
        # frontend can show "your value" alongside each category's typical
        # range without a second API call.
        sample_values = {
            p: float(X_row[p].iloc[0]) for p in BASE_PARAMS if p in X_row.columns
        }

        return narrative, top_features, waterfall, sample_values, self.category_ranges


@lru_cache
def get_explanation_service() -> ExplanationService:
    return ExplanationService(settings.model_dir_path)