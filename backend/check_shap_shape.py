import numpy as np
import joblib
import pandas as pd

# Load your actual production artifacts
model = joblib.load("ml_artifacts/xgb_model.pkl")
explainer = joblib.load("ml_artifacts/shap_explainer.pkl")
feature_columns = joblib.load("ml_artifacts/feature_columns.pkl")
label_encoder = joblib.load("ml_artifacts/label_encoder.pkl")

print("Feature columns:", feature_columns)
print("Label classes:", label_encoder.classes_)

# Build one dummy row matching your feature columns
# Replace these with a real sample if you have one handy (e.g. from your test CSV)
X_row = pd.DataFrame([np.random.rand(len(feature_columns))], columns=feature_columns)

shap_values = explainer.shap_values(X_row)

print("\nshap_values type:", type(shap_values))
print("shap_values shape:", np.array(shap_values).shape)
print("expected_value type:", type(explainer.expected_value))
print("expected_value:", explainer.expected_value)