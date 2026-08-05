from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.db_models import WaterReading


def create_reading(db: Session, reading_data: dict) -> WaterReading:
    reading = WaterReading(**reading_data)
    db.add(reading)
    db.commit()
    db.refresh(reading)
    return reading


def get_readings_by_station(db: Session, station_id: str, limit: int = 100):
    """Ordered oldest-to-newest by year -- needed for rolling feature computation."""
    return (
        db.query(WaterReading)
        .filter(WaterReading.station_id == station_id)
        .order_by(WaterReading.year.asc())
        .limit(limit)
        .all()
    )


def get_all_stations_summary(db: Session):
    stations = db.query(WaterReading.station_id).distinct().all()
    summaries = []
    for (station_id,) in stations:
        latest = (
            db.query(WaterReading)
            .filter(WaterReading.station_id == station_id)
            .order_by(WaterReading.year.desc())
            .first()
        )
        count = (
            db.query(func.count(WaterReading.id))
            .filter(WaterReading.station_id == station_id)
            .scalar()
        )
        summaries.append({
            "station_id": station_id,
            "latest_year": latest.year if latest else None,
            "latest_prediction": latest.predicted_source if latest else None,
            "total_readings": count,
        })
    return summaries


def get_history(db: Session, station_id: str = None, limit: int = 200):
    query = db.query(WaterReading)
    if station_id:
        query = query.filter(WaterReading.station_id == station_id)
    return query.order_by(WaterReading.year.desc()).limit(limit).all()
