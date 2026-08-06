# from fastapi import APIRouter, Depends
# from sqlalchemy.orm import Session

# from app.models.schemas import StationSummary
# from app.db.database import get_db
# from app.db import crud

# router = APIRouter(tags=["stations"])


# @router.get("/stations", response_model=list[StationSummary])
# def list_stations(db: Session = Depends(get_db)):
#     return crud.get_all_stations_summary(db)


from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.models.schemas import StationSummary
from app.db.database import get_db
from app.db import crud

router = APIRouter(tags=["stations"])


@router.get("/stations", response_model=list[StationSummary])
def list_stations(db: Session = Depends(get_db)):
    return crud.get_all_stations_summary(db)


@router.delete("/stations/{station_id}")
def delete_station(station_id: str, db: Session = Depends(get_db)):
    """Deletes a station/lake and all of its readings."""
    deleted_count = crud.delete_station(db, station_id)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail=f"Station '{station_id}' not found")
    return {"station_id": station_id, "rows_deleted": deleted_count, "message": "Station deleted"}