from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import WaterSampleInput, ExplanationResponse
from app.services.inference_service import get_inference_service, InferenceService
from app.services.explanation_service import get_explanation_service, ExplanationService
from app.api.routes_predict import _reading_to_dict
from app.db.database import get_db
from app.db import crud

router = APIRouter(tags=["explanation"])


@router.post("/explain", response_model=ExplanationResponse)
def explain(
    sample: WaterSampleInput,
    db: Session = Depends(get_db),
    inference: InferenceService = Depends(get_inference_service),
    explanation: ExplanationService = Depends(get_explanation_service),
):
    if not inference.is_ready() or not explanation.is_ready():
        raise HTTPException(
            status_code=503,
            detail="Model/explainer not available yet. Run the ML pipeline first.",
        )

    prior_readings = crud.get_readings_by_station(db, sample.station_id)
    history_rows = [
        _reading_to_dict(r) for r in prior_readings if r.year != sample.year
    ]

    try:
        predicted_class, confidence, X_row = inference.predict(sample.model_dump(), history_rows)
        narrative, top_features = explanation.explain(X_row, predicted_class)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    return ExplanationResponse(
        station_id=sample.station_id,
        predicted_source=predicted_class,
        narrative=narrative,
        top_features=top_features,
    )
