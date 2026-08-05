import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import numpy as np
import pandas as pd
from src.models.train_rf import train_random_forest


def test_train_random_forest_runs():
    X = pd.DataFrame(np.random.rand(50, 4), columns=["a", "b", "c", "d"])
    y = pd.Series(np.random.choice(["classA", "classB"], 50))
    model, X_train, X_test, y_train, y_test = train_random_forest(X, y)
    assert hasattr(model, "predict")
    preds = model.predict(X_test)
    assert len(preds) == len(y_test)
