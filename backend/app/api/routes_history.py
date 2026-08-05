from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.models.schemas import HistoryRecord
from app.core.parameters import AVAILABLE_PARAMETERS
from app.db.database import get_db
from app.db import crud

router = APIRouter(tags=["history"])


def _reading_to_history_record(r) -> HistoryRecord:
    data = {
        "station_id": r.station_id,
        "year": r.year,
        "predicted_source": r.predicted_source or "unclassified",
        "confidence": r.confidence or 0.0,
    }
    for p in AVAILABLE_PARAMETERS:
        data[f"{p}_min"] = getattr(r, f"{p}_min", None)
        data[f"{p}_max"] = getattr(r, f"{p}_max", None)
    return HistoryRecord(**data)


@router.get("/history", response_model=list[HistoryRecord])
def get_history(
    station_id: Optional[str] = Query(None),
    limit: int = Query(200, le=1000),
    db: Session = Depends(get_db),
):
    records = crud.get_history(db, station_id=station_id, limit=limit)
    return [_reading_to_history_record(r) for r in records]
