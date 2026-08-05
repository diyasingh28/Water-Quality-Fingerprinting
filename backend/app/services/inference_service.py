"""
Loads the trained model + feature pipeline artifacts and runs predictions
using the real feature engineering (feature_engineering.py) built to match
training time exactly.

Expects these files in ml_artifacts/ (copied from
ml-pipeline/src/models/model_registry/ after running run_pipeline.py):
    - xgb_model.pkl
    - label_encoder.pkl
    - feature_columns.pkl
    - shap_explainer.pkl
"""

import joblib
import numpy as np
from pathlib import Path
from functools import lru_cache

from app.core.config import settings
from app.services.feature_engineering import build_feature_row


class InferenceService:
    def __init__(self, model_dir: Path):
        self.model_dir = model_dir
        self.model = None
        self.label_encoder = None
        self.feature_columns = None
        self._load_artifacts()

    def _load_artifacts(self):
        try:
            self.model = joblib.load(self.model_dir / "xgb_model.pkl")
            self.label_encoder = joblib.load(self.model_dir / "label_encoder.pkl")
            self.feature_columns = joblib.load(self.model_dir / "feature_columns.pkl")
        except FileNotFoundError:
            # Artifacts not trained yet -- API will return a clear error on /predict
            self.model = None

    def is_ready(self) -> bool:
        return self.model is not None

    def _align_to_training_columns(self, df):
        for col in self.feature_columns:
            if col not in df.columns:
                df[col] = 0
        return df[self.feature_columns]

    def predict(self, current_sample: dict, history_rows: list[dict]):
        if not self.is_ready():
            raise RuntimeError(
                "Model not trained yet. Run ml-pipeline/run_pipeline.py "
                "and copy artifacts into backend/ml_artifacts/"
            )
        X_full = build_feature_row(current_sample, history_rows)
        X = self._align_to_training_columns(X_full.copy())

        pred_encoded = self.model.predict(X)[0]
        proba = self.model.predict_proba(X)[0]
        predicted_class = self.label_encoder.inverse_transform([pred_encoded])[0]
        confidence = float(np.max(proba))
        return predicted_class, confidence, X


@lru_cache
def get_inference_service() -> InferenceService:
    return InferenceService(settings.model_dir_path)
