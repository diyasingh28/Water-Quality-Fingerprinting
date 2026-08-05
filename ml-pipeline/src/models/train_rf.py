"""Train a Random Forest classifier on fingerprint feature vectors."""

import joblib
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split, GridSearchCV

MODEL_DIR = Path(__file__).parent / "model_registry"
MODEL_DIR.mkdir(exist_ok=True)


def train_random_forest(X, y, tune: bool = False):
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    if tune:
        param_grid = {
            "n_estimators": [100, 200, 300],
            "max_depth": [None, 10, 20, 30],
            "min_samples_split": [2, 5, 10],
        }
        base_model = RandomForestClassifier(random_state=42, class_weight="balanced")
        search = GridSearchCV(base_model, param_grid, cv=5, scoring="f1_weighted", n_jobs=-1)
        search.fit(X_train, y_train)
        model = search.best_estimator_
        print("Best params:", search.best_params_)
    else:
        model = RandomForestClassifier(
            n_estimators=200, max_depth=20, random_state=42, class_weight="balanced"
        )
        model.fit(X_train, y_train)

    joblib.dump(model, MODEL_DIR / "rf_model.pkl")
    return model, X_train, X_test, y_train, y_test


if __name__ == "__main__":
    print("Run this via run_pipeline.py — it needs fingerprint vectors as input.")
