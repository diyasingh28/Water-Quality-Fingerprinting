"""Exposes per-station CSV/PDF report downloads using report_service.py."""

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.db.database import get_db
from app.db import crud
from app.services.report_service import generate_csv_report, generate_pdf_report

router = APIRouter(tags=["reports"])


@router.get("/reports/{station_id}/csv")
def download_csv_report(station_id: str, db: Session = Depends(get_db)):
    readings = crud.get_readings_by_station(db, station_id)
    if not readings:
        raise HTTPException(status_code=404, detail=f"No readings found for station {station_id}")

    buffer = generate_csv_report(readings)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="text/csv",
        headers={"Content-Disposition": f'attachment; filename="station_{station_id}_report.csv"'},
    )


@router.get("/reports/{station_id}/pdf")
def download_pdf_report(station_id: str, db: Session = Depends(get_db)):
    readings = crud.get_readings_by_station(db, station_id)
    if not readings:
        raise HTTPException(status_code=404, detail=f"No readings found for station {station_id}")

    buffer = generate_pdf_report(station_id, readings)
    return StreamingResponse(
        iter([buffer.getvalue()]),
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="station_{station_id}_report.pdf"'},
    )