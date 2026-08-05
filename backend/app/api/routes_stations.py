from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.models.schemas import StationSummary
from app.db.database import get_db
from app.db import crud

router = APIRouter(tags=["stations"])


@router.get("/stations", response_model=list[StationSummary])
def list_stations(db: Session = Depends(get_db)):
    return crud.get_all_stations_summary(db)
