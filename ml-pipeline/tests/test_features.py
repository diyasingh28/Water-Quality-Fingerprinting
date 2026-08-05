import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from src.features.fingerprint_builder import add_ratio_features, rule_based_label


def test_add_ratio_features():
    df = pd.DataFrame({"bod": [10], "cod": [20], "tds": [100], "conductivity": [200],
                        "nitrate": [5], "dissolved_oxygen": [4]})
    out = add_ratio_features(df)
    assert "bod_to_cod_ratio" in out.columns
    assert out["bod_to_cod_ratio"].iloc[0] == 0.5


def test_rule_based_label_sewage():
    row = pd.Series({"bod": 40, "fecal_coliform": 6000, "dissolved_oxygen": 2})
    assert rule_based_label(row) == "sewage_domestic"
