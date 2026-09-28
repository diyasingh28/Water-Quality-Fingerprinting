from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import WaterSampleInput, PredictionResponse
from app.services.inference_service import get_inference_service, InferenceService
from app.core.parameters import AVAILABLE_PARAMETERS
from app.db.database import get_db
from app.db import crud

import json
from app.services.anomaly_service import compute_anomaly

router = APIRouter(tags=["prediction"])


def _reading_to_dict(reading) -> dict:
    """Converts a stored WaterReading ORM row into the plain dict shape
    feature_engineering.py expects (station_id, year, {param}_min/_max)."""
    out = {"station_id": reading.station_id, "year": reading.year}
    for p in AVAILABLE_PARAMETERS:
        out[f"{p}_min"] = getattr(reading, f"{p}_min")
        out[f"{p}_max"] = getattr(reading, f"{p}_max")
    return out


@router.post("/predict", response_model=PredictionResponse)
def predict(
    sample: WaterSampleInput,
    db: Session = Depends(get_db),
    inference: InferenceService = Depends(get_inference_service),
):
    if not inference.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Model not trained yet. Run the ML pipeline first and copy "
                   "artifacts into backend/ml_artifacts/.",
        )

    prior_readings = crud.get_readings_by_station(db, sample.station_id)
    history_rows = [
        _reading_to_dict(r) for r in prior_readings if r.year != sample.year
    ]

    # try:
    #     predicted_class, confidence, _ = inference.predict(sample.model_dump(), history_rows)
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=str(e))

    # crud.create_reading(db, {
    #     **sample.model_dump(),
    #     "predicted_source": predicted_class,
    #     "confidence": confidence,
    #     "source_type": "dataset",
    # })

    # return PredictionResponse(
    #     station_id=sample.station_id,
    #     year=sample.year,
    #     predicted_source=predicted_class,
    #     confidence=confidence,
    # )

    try:
        predicted_class, confidence, X_row = inference.predict(sample.model_dump(), history_rows)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    anomaly = compute_anomaly(sample.model_dump(), history_rows)

    crud.create_reading(db, {
        **sample.model_dump(),
        "predicted_source": predicted_class,
        "confidence": confidence,
        "source_type": "dataset",
        "is_anomaly": anomaly["is_anomaly"],
        "anomaly_details": json.dumps(anomaly["anomalies"]),
    })

    return PredictionResponse(
        station_id=sample.station_id,
        year=sample.year,
        predicted_source=predicted_class,
        confidence=confidence,
    )
