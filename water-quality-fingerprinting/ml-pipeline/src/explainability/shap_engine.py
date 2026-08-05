"""SHAP-based explainability for the trained pollution-source classifiers."""

import joblib
import shap
from pathlib import Path

MODEL_DIR = Path(__file__).parent.parent / "models" / "model_registry"


def build_explainer(model, X_background):
    """
    Build a SHAP TreeExplainer for RF/XGBoost models (both are tree-based,
    so TreeExplainer is exact and fast — no need for KernelExplainer here).

    Uses feature_perturbation="tree_path_dependent" instead of passing a
    background dataset — newer XGBoost versions can produce categorical
    splits that SHAP's interventional (background-data) mode doesn't
    support yet. Path-dependent mode works directly from the tree
    structure and doesn't hit that limitation.
    """
    explainer = shap.TreeExplainer(model, feature_perturbation="tree_path_dependent")
    return explainer


def compute_shap_values(explainer, X):
    """Compute SHAP values for a batch of samples."""
    return explainer.shap_values(X)


def save_explainer(explainer, filename: str = "shap_explainer.pkl"):
    joblib.dump(explainer, MODEL_DIR / filename)


def load_explainer(filename: str = "shap_explainer.pkl"):
    return joblib.load(MODEL_DIR / filename)


def explain_single_prediction(explainer, X_row, feature_names):
    """
    Returns a sorted list of (feature, shap_value) for one sample —
    used by the API's /explain endpoint.
    """
    shap_values = explainer.shap_values(X_row)
    # shap_values shape depends on binary vs multiclass; handle both
    values = shap_values[0] if isinstance(shap_values, list) else shap_values
    pairs = list(zip(feature_names, values.flatten()))
    pairs.sort(key=lambda x: abs(x[1]), reverse=True)
    return pairs
