"""Train an XGBoost classifier on fingerprint feature vectors."""

import joblib
from pathlib import Path
import xgboost as xgb
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import LabelEncoder

MODEL_DIR = Path(__file__).parent / "model_registry"
MODEL_DIR.mkdir(exist_ok=True)


def train_xgboost(X, y, tune: bool = False):
    label_encoder = LabelEncoder()
    y_encoded = label_encoder.fit_transform(y)
    joblib.dump(label_encoder, MODEL_DIR / "label_encoder.pkl")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y_encoded, test_size=0.2, random_state=42, stratify=y_encoded
    )

    if tune:
        param_grid = {
            "n_estimators": [100, 200, 300],
            "max_depth": [3, 5, 7],
            "learning_rate": [0.01, 0.1, 0.2],
        }
        base_model = xgb.XGBClassifier(
            random_state=42, eval_metric="mlogloss", use_label_encoder=False
        )
        search = GridSearchCV(base_model, param_grid, cv=5, scoring="f1_weighted", n_jobs=-1)
        search.fit(X_train, y_train)
        model = search.best_estimator_
        print("Best params:", search.best_params_)
    else:
        model = xgb.XGBClassifier(
            n_estimators=200,
            max_depth=5,
            learning_rate=0.1,
            random_state=42,
            eval_metric="mlogloss",
        )
        model.fit(X_train, y_train)

    joblib.dump(model, MODEL_DIR / "xgb_model.pkl")
    return model, X_train, X_test, y_train, y_test, label_encoder


if __name__ == "__main__":
    print("Run this via run_pipeline.py — it needs fingerprint vectors as input.")
