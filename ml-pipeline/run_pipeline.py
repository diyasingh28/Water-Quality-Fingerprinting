"""
End-to-end Phase 1 pipeline:
ingest -> clean -> engineer fingerprint features -> train RF + XGBoost ->
evaluate -> SHAP explain -> save all artifacts to model_registry/

Usage:
    python run_pipeline.py
"""

import sys
import joblib
import pandas as pd
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.ingestion.nwmp_lake_loader import NWMPLakeSource
from src.preprocessing.cleaning import clean_pipeline
from src.preprocessing.alignment import align_by_station_year
from src.features.fingerprint_builder import build_fingerprint_vectors
from src.models.train_rf import train_random_forest
from src.models.train_xgboost import train_xgboost
from src.models.evaluate import evaluate_model
from src.explainability.shap_engine import build_explainer, save_explainer, compute_shap_values
from src.explainability.plots import save_summary_plot, save_bar_plot
from src.utils.config import PROCESSED_DATA_DIR, FINGERPRINT_DATA_DIR, MODEL_REGISTRY_DIR, RAW_DATA_DIR
from src.utils.logger import get_logger

logger = get_logger()

# The combined, name-normalized multi-year NWMP lake dataset.
# See docs/phase1_report.md for how this file is produced from the
# individual yearly CPCB CSVs.
NWMP_COMBINED_FILE = RAW_DATA_DIR / "nwmp_lakes_2017_2022_combined.csv"

NON_FEATURE_COLS = ["station_id", "State Name", "Type Water Body", "year", "pollution_source"]


def main():
    logger.info("Step 1/6 — Ingesting data")
    loader = NWMPLakeSource(str(NWMP_COMBINED_FILE))
    raw_df = loader.fetch()
    logger.info(f"Loaded {len(raw_df)} raw rows")

    logger.info("Step 2/6 — Cleaning + aligning")
    clean_df = clean_pipeline(raw_df)
    aligned_df = align_by_station_year(clean_df)
    PROCESSED_DATA_DIR.mkdir(parents=True, exist_ok=True)
    aligned_df.to_csv(PROCESSED_DATA_DIR / "cleaned_aligned.csv", index=False)

    logger.info("Step 3/6 — Building fingerprint feature vectors")
    fingerprint_df = build_fingerprint_vectors(aligned_df)
    FINGERPRINT_DATA_DIR.mkdir(parents=True, exist_ok=True)
    fingerprint_df.to_csv(FINGERPRINT_DATA_DIR / "fingerprint_vectors.csv", index=False)
    logger.info(f"Built {fingerprint_df.shape[1] - len(NON_FEATURE_COLS)} features")

    feature_cols = [
        c for c in fingerprint_df.columns
        if c not in NON_FEATURE_COLS and pd.api.types.is_numeric_dtype(fingerprint_df[c])
    ]
    X = fingerprint_df[feature_cols].fillna(0)
    y = fingerprint_df["pollution_source"]

    logger.info("Step 4/6 — Training models")
    rf_model, X_train_rf, X_test_rf, y_train_rf, y_test_rf = train_random_forest(X, y)
    xgb_model, X_train_xgb, X_test_xgb, y_train_xgb, y_test_xgb, label_encoder = train_xgboost(X, y)

    logger.info("Step 5/6 — Evaluating models")
    class_names = sorted(y.unique())
    evaluate_model(rf_model, X_test_rf, y_test_rf, "random_forest", class_names=class_names)
    evaluate_model(xgb_model, X_test_xgb, y_test_xgb, "xgboost", class_names=list(label_encoder.classes_))

    logger.info("Step 6/6 — Running SHAP explainability (on XGBoost model)")
    explainer = build_explainer(xgb_model, X_train_xgb)
    save_explainer(explainer)
    shap_values = compute_shap_values(explainer, X_test_xgb)
    save_summary_plot(shap_values, X_test_xgb)
    save_bar_plot(shap_values, X_test_xgb)

    # Persist feature column order — required by backend at inference time
    joblib.dump(feature_cols, MODEL_REGISTRY_DIR / "feature_columns.pkl")

    logger.info("Pipeline complete. Artifacts saved to src/models/model_registry/")
    logger.info("Copy model_registry/*.pkl into backend/ml_artifacts/ to serve via API.")


if __name__ == "__main__":
    main()
