"""Central config for file paths and pipeline settings."""

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent  # ml-pipeline/

RAW_DATA_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DATA_DIR = BASE_DIR / "data" / "processed"
FINGERPRINT_DATA_DIR = BASE_DIR / "data" / "fingerprints"
MODEL_REGISTRY_DIR = BASE_DIR / "src" / "models" / "model_registry"

# Default filenames — update once you know your actual downloaded dataset name
CPCB_RAW_FILE = RAW_DATA_DIR / "cpcb_water_quality.csv"
TNPCB_RAW_FILE = RAW_DATA_DIR / "tnpcb_water_quality.csv"

RANDOM_SEED = 42
