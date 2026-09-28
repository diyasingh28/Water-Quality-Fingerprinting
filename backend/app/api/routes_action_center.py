"""Aggregates each station's latest prediction, computed severity, and
tracked remediation status -- powers the Action Center page."""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
import json

from app.db.database import get_db
from app.db import crud
from app.services.explanation_service import get_explanation_service, ExplanationService
from app.services.severity_service import compute_severity

router = APIRouter(tags=["action-center"])


class StationActionItem(BaseModel):
    station_id: str
    station_name: str | None = None
    predicted_source: str
    confidence: float | None = None
    year: int
    severity_score: float
    severity_label: str
    actionable: bool
    is_anomaly: bool = False
    anomaly_summary: str | None = None
    status: str
    latitude: float | None = None
    longitude: float | None = None


class StatusUpdateRequest(BaseModel):
    status: str
    note: str | None = None


def _to_item(reading, category_ranges, status) -> StationActionItem:
    severity = compute_severity(reading, category_ranges)
    is_anomaly = bool(getattr(reading, "is_anomaly", False))

    anomaly_summary = None
    raw = getattr(reading, "anomaly_details", None)
    if is_anomaly and raw:
        try:
            details = json.loads(raw)
            if details:
                top = details[0]
                anomaly_summary = (
                    f"{top['parameter'].replace('_', ' ').title()} unusual "
                    f"vs. this station's own history (z={top['z_score']})"
                )
        except Exception:
            pass

    return StationActionItem(
        station_id=reading.station_id,
        station_name=getattr(reading, "station_name", None),
        predicted_source=reading.predicted_source or "unclassified",
        confidence=getattr(reading, "confidence", None),
        year=reading.year,
        severity_score=severity["score"],
        severity_label=severity["label"],
        actionable=severity["actionable"],
        is_anomaly=is_anomaly,
        anomaly_summary=anomaly_summary,
        status=status,
        latitude=getattr(reading, "latitude", None),
        longitude=getattr(reading, "longitude", None),
    )


@router.get("/action-center", response_model=list[StationActionItem])
def list_action_items(
    db: Session = Depends(get_db),
    explanation: ExplanationService = Depends(get_explanation_service),
):
    readings = crud.get_latest_readings(db)
    category_ranges = explanation.category_ranges or {}

    items = []
    for r in readings:
        status_row = crud.get_station_status(db, r.station_id)
        status = status_row.status if status_row else "unaddressed"
        items.append(_to_item(r, category_ranges, status))

    status_rank = {"unaddressed": 0, "planned": 1, "completed": 2}
    items.sort(key=lambda i: (
        0 if i.actionable else 1,
        status_rank.get(i.status, 0),
        -i.severity_score,
    ))
    return items


@router.patch("/action-center/{station_id}/status", response_model=StationActionItem)
def update_status(
    station_id: str,
    body: StatusUpdateRequest,
    db: Session = Depends(get_db),
    explanation: ExplanationService = Depends(get_explanation_service),
):
    if body.status not in ("unaddressed", "planned", "completed"):
        raise HTTPException(status_code=400, detail="status must be unaddressed, planned, or completed")

    crud.upsert_station_status(db, station_id, body.status, body.note)

    readings = crud.get_readings_by_station(db, station_id)
    if not readings:
        raise HTTPException(status_code=404, detail=f"No readings found for station {station_id}")
    latest = max(readings, key=lambda r: r.year)

    return _to_item(latest, explanation.category_ranges or {}, body.status)