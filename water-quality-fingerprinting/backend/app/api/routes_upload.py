import pandas as pd
import io
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import UploadResponse
from app.services.inference_service import get_inference_service, InferenceService
from app.core.parameters import AVAILABLE_PARAMETERS
from app.api.routes_predict import _reading_to_dict
from app.db.database import get_db
from app.db import crud

router = APIRouter(tags=["upload"])

REQUIRED_COLUMNS = ["station_id", "year"] + [
    f"{p}_min" for p in AVAILABLE_PARAMETERS
] + [f"{p}_max" for p in AVAILABLE_PARAMETERS]


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

    # Process in chronological order per station so rolling features build
    # up correctly row by row, same as at training time.
    df = df.sort_values(["station_id", "year"])

    predictions_count = 0
    for _, row in df.iterrows():
        sample = row[REQUIRED_COLUMNS].to_dict()

        prior_readings = crud.get_readings_by_station(db, sample["station_id"])
        history_rows = [
            _reading_to_dict(r) for r in prior_readings if r.year != sample["year"]
        ]

        try:
            predicted_class, confidence, _ = inference.predict(sample, history_rows)
        except Exception:
            continue

        crud.create_reading(db, {
            **sample,
            "predicted_source": predicted_class,
            "confidence": confidence,
            "source_type": "dataset",
        })
        predictions_count += 1

    return UploadResponse(
        rows_processed=len(df),
        predictions_generated=predictions_count,
        message="Upload processed successfully.",
    )
