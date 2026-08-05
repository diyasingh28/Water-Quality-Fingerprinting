from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import WaterSampleInput, PredictionResponse
from app.services.inference_service import get_inference_service, InferenceService
from app.core.parameters import AVAILABLE_PARAMETERS
from app.db.database import get_db
from app.db import crud

router = APIRouter(tags=["prediction"])

# Parameters that can only come from a lab test, not a live sensor.
LAB_ONLY_PARAMS = ["bod", "fecal_coliform", "total_coliform"]


def _reading_to_dict(reading) -> dict:
    """Converts a stored WaterReading ORM row into the plain dict shape
    feature_engineering.py expects (station_id, year, {param}_min/_max)."""
    out = {"station_id": reading.station_id, "year": reading.year}
    for p in AVAILABLE_PARAMETERS:
        out[f"{p}_min"] = getattr(reading, f"{p}_min")
        out[f"{p}_max"] = getattr(reading, f"{p}_max")
    return out


def _fill_missing_lab_values(sample: dict, db: Session) -> tuple[dict, str]:
    """
    If the request omitted BOD/fecal coliform/total coliform (e.g. a
    real-time ESP32 sensor reading that can only provide the 5 live
    parameters), fall back to this station's most recent stored reading
    that actually has lab values. This implements the hybrid design:
    real-time sensor data + periodic lab test data feeding the same model.

    Returns (filled_sample, source_label) where source_label is one of:
        "provided"                    -- all lab values were in the request
        "fallback_from_last_lab_test" -- missing values filled from history
        "no_lab_data_available"       -- missing values, no history to use (defaults to 0)
    """
    missing = [
        p for p in LAB_ONLY_PARAMS
        if sample.get(f"{p}_min") is None or sample.get(f"{p}_max") is None
    ]
    if not missing:
        return sample, "provided"

    prior_readings = crud.get_readings_by_station(db, sample["station_id"])
    # Search newest-to-oldest for the most recent reading that actually has
    # real lab values (not itself falling back to defaults).
    for reading in reversed(prior_readings):
        has_all_lab_values = all(
            getattr(reading, f"{p}_min") is not None and getattr(reading, f"{p}_max") is not None
            for p in LAB_ONLY_PARAMS
        )
        if has_all_lab_values:
            for p in LAB_ONLY_PARAMS:
                sample[f"{p}_min"] = getattr(reading, f"{p}_min")
                sample[f"{p}_max"] = getattr(reading, f"{p}_max")
            return sample, "fallback_from_last_lab_test"

    # No usable lab history at all -- default to 0 rather than error out,
    # but flag this clearly so the caller/UI can warn the user.
    for p in missing:
        sample[f"{p}_min"] = 0.0
        sample[f"{p}_max"] = 0.0
    return sample, "no_lab_data_available"


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

    sample_dict = sample.model_dump()
    sample_dict, lab_source = _fill_missing_lab_values(sample_dict, db)

    prior_readings = crud.get_readings_by_station(db, sample.station_id)
    history_rows = [
        _reading_to_dict(r) for r in prior_readings if r.year != sample.year
    ]

    try:
        predicted_class, confidence, _ = inference.predict(sample_dict, history_rows)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    crud.create_reading(db, {
        **sample_dict,
        "predicted_source": predicted_class,
        "confidence": confidence,
        "source_type": "iot" if lab_source != "provided" else "dataset",
    })

    return PredictionResponse(
        station_id=sample.station_id,
        year=sample.year,
        predicted_source=predicted_class,
        confidence=confidence,
        lab_values_source=lab_source,
    )
