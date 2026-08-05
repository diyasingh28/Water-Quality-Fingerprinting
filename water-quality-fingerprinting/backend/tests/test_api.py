import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_stations_empty_db():
    response = client.get("/stations")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_predict_without_model_returns_503_or_success():
    payload = {
        "station_id": "TEST_LAKE",
        "year": 2022,
        "ph_min": 6.8, "ph_max": 7.5,
        "dissolved_oxygen_min": 4.5, "dissolved_oxygen_max": 7.0,
        "bod_min": 1.5, "bod_max": 3.0,
        "conductivity_min": 200, "conductivity_max": 400,
        "nitrate_min": 0.5, "nitrate_max": 2.0,
        "fecal_coliform_min": 20, "fecal_coliform_max": 100,
        "total_coliform_min": 50, "total_coliform_max": 200,
        "temperature_min": 22, "temperature_max": 28,
    }
    response = client.post("/predict", json=payload)
    # Before a model is trained, expect 503; after training, expect 200.
    assert response.status_code in (200, 503)
