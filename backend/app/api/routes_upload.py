import pandas as pd
import io
import logging
import json
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import UploadResponse
from app.services.inference_service import get_inference_service, InferenceService
from app.core.parameters import AVAILABLE_PARAMETERS
from app.api.routes_predict import _reading_to_dict
from app.db.database import get_db
from app.db import crud
from app.services.geocoding_service import geocode_station
from app.services.anomaly_service import compute_anomaly

router = APIRouter(tags=["upload"])
logger = logging.getLogger("uvicorn.error")

REQUIRED_COLUMNS = ["station_id", "year"] + [
    f"{p}_min" for p in AVAILABLE_PARAMETERS
] + [f"{p}_max" for p in AVAILABLE_PARAMETERS]

NUMERIC_COLUMNS = [c for c in REQUIRED_COLUMNS if c not in ("station_id",)]


def _clean_numeric_columns(df: pd.DataFrame) -> pd.DataFrame:
    """
    Real CPCB lab data often reports values below the instrument's
    detection threshold as text (e.g. "BDL" = Below Detection Limit,
    or "NIL", "ND", "-"), not a clean number. These represent a
    negligible/near-zero amount, not missing data, so we coerce them to 0
    rather than dropping the row entirely.
    """
    df = df.copy()
    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
    return df


@router.post("/upload", response_model=UploadResponse)
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    inference: InferenceService = Depends(get_inference_service),
):
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are supported.")

    contents = await file.read()
    df = pd.read_csv(io.BytesIO(contents))

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

    if not inference.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Model not trained yet. Run the ML pipeline first.",
        )

    df = _clean_numeric_columns(df)
    df = df.sort_values(["station_id", "year"])

    geocode_cache = {}

    predictions_count = 0
    errors = []
    for _, row in df.iterrows():
        sample = row[REQUIRED_COLUMNS].to_dict()
        if "station_name" in df.columns:
            sample["station_name"] = row["station_name"]
        sample = {
            k: (v.item() if hasattr(v, "item") else v) for k, v in sample.items()
        }

        prior_readings = crud.get_readings_by_station(db, sample["station_id"])
        history_rows = [
            _reading_to_dict(r) for r in prior_readings if r.year != sample["year"]
        ]

        station_id = sample["station_id"]
        existing_coords = next(
            (
                (r.latitude, r.longitude)
                for r in prior_readings
                if r.latitude is not None and r.longitude is not None
            ),
            None,
        )

        if existing_coords:
            sample["latitude"], sample["longitude"] = existing_coords
        elif station_id in geocode_cache:
            sample["latitude"], sample["longitude"] = geocode_cache[station_id]
        else:
            query = sample.get("station_name") or station_id
            lat, lon = geocode_station(query)
            geocode_cache[station_id] = (lat, lon)
            sample["latitude"], sample["longitude"] = lat, lon
            if lat is None:
                logger.warning(f"Could not geocode station {station_id} ({query!r})")

        try:
            predicted_class, confidence, X_row = inference.predict(sample, history_rows)
        except Exception as e:
            logger.error(f"Prediction failed for {sample.get('station_id')} "
                        f"year={sample.get('year')}: {e}")
            errors.append(f"{sample.get('station_id')} ({sample.get('year')}): {e}")
            continue

        anomaly = compute_anomaly(sample, history_rows)

        reading_payload = {
            **sample,
            "predicted_source": predicted_class,
            "confidence": confidence,
            "source_type": "dataset",
            "is_anomaly": anomaly["is_anomaly"],
            "anomaly_details": json.dumps(anomaly["anomalies"]),
        }

        existing = next((r for r in prior_readings if r.year == sample["year"]), None)
        if existing:
            crud.update_reading(db, existing, reading_payload)
            logger.info(f"Updated existing reading for {sample['station_id']} "
                        f"year={sample['year']} (was a duplicate upload)")
        else:
            crud.create_reading(db, reading_payload)
        predictions_count += 1

    message = "Upload processed successfully."
    if errors:
        message += f" {len(errors)} row(s) failed -- see server logs for details."

    return UploadResponse(
        rows_processed=len(df),
        predictions_generated=predictions_count,
        message=message,
    )