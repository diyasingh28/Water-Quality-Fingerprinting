# import pandas as pd
# import io
# from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
# from sqlalchemy.orm import Session

# from app.models.schemas import UploadResponse
# from app.services.inference_service import get_inference_service, InferenceService
# from app.core.parameters import AVAILABLE_PARAMETERS
# from app.api.routes_predict import _reading_to_dict
# from app.db.database import get_db
# from app.db import crud

# router = APIRouter(tags=["upload"])

# REQUIRED_COLUMNS = ["station_id", "year"] + [
#     f"{p}_min" for p in AVAILABLE_PARAMETERS
# ] + [f"{p}_max" for p in AVAILABLE_PARAMETERS]


# @router.post("/upload", response_model=UploadResponse)
# async def upload_csv(
#     file: UploadFile = File(...),
#     db: Session = Depends(get_db),
#     inference: InferenceService = Depends(get_inference_service),
# ):
#     if not file.filename.endswith(".csv"):
#         raise HTTPException(status_code=400, detail="Only CSV files are supported.")

#     contents = await file.read()
#     df = pd.read_csv(io.BytesIO(contents))

#     missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
#     if missing:
#         raise HTTPException(status_code=400, detail=f"Missing columns: {missing}")

#     if not inference.is_ready():
#         raise HTTPException(
#             status_code=503,
#             detail="Model not trained yet. Run the ML pipeline first.",
#         )

#     # Process in chronological order per station so rolling features build
#     # up correctly row by row, same as at training time.
#     df = df.sort_values(["station_id", "year"])

#     predictions_count = 0
#     for _, row in df.iterrows():
#         sample = row[REQUIRED_COLUMNS].to_dict()

#         prior_readings = crud.get_readings_by_station(db, sample["station_id"])
#         history_rows = [
#             _reading_to_dict(r) for r in prior_readings if r.year != sample["year"]
#         ]

#         try:
#             predicted_class, confidence, _ = inference.predict(sample, history_rows)
#         except Exception:
#             continue

#         crud.create_reading(db, {
#             **sample,
#             "predicted_source": predicted_class,
#             "confidence": confidence,
#             "source_type": "dataset",
#         })
#         predictions_count += 1

#     return UploadResponse(
#         rows_processed=len(df),
#         predictions_generated=predictions_count,
#         message="Upload processed successfully.",
#     )

import pandas as pd
import io
import logging
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import UploadResponse
from app.services.inference_service import get_inference_service, InferenceService
from app.core.parameters import AVAILABLE_PARAMETERS
from app.api.routes_predict import _reading_to_dict
from app.db.database import get_db
from app.db import crud

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

    # Process in chronological order per station so rolling features build
    # up correctly row by row, same as at training time.
    df = df.sort_values(["station_id", "year"])

    predictions_count = 0
    errors = []
    for _, row in df.iterrows():
        sample = row[REQUIRED_COLUMNS].to_dict()
        # Cast numpy scalar types (int64/float64) to native Python types --
        # SQLAlchemy/sqlite can otherwise reject numpy types on insert.
        sample = {
            k: (v.item() if hasattr(v, "item") else v) for k, v in sample.items()
        }

        prior_readings = crud.get_readings_by_station(db, sample["station_id"])
        history_rows = [
            _reading_to_dict(r) for r in prior_readings if r.year != sample["year"]
        ]

        try:
            predicted_class, confidence, _ = inference.predict(sample, history_rows)
        except Exception as e:
            # Log the real reason instead of silently swallowing it --
            # a previous version of this endpoint hid all row-level errors,
            # making failures invisible even in the server logs.
            logger.error(f"Prediction failed for {sample.get('station_id')} "
                         f"year={sample.get('year')}: {e}")
            errors.append(f"{sample.get('station_id')} ({sample.get('year')}): {e}")
            continue

        crud.create_reading(db, {
            **sample,
            "predicted_source": predicted_class,
            "confidence": confidence,
            "source_type": "dataset",
        })
        predictions_count += 1

    message = "Upload processed successfully."
    if errors:
        message += f" {len(errors)} row(s) failed -- see server logs for details."

    return UploadResponse(
        rows_processed=len(df),
        predictions_generated=predictions_count,
        message=message,
    )