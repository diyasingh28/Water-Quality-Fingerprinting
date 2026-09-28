# from sqlalchemy.orm import Session
# from sqlalchemy import func

# from app.models.db_models import WaterReading


# def create_reading(db: Session, reading_data: dict) -> WaterReading:
#     reading = WaterReading(**reading_data)
#     db.add(reading)
#     db.commit()
#     db.refresh(reading)
#     return reading


# def get_readings_by_station(db: Session, station_id: str, limit: int = 100):
#     """Ordered oldest-to-newest by year -- needed for rolling feature computation."""
#     return (
#         db.query(WaterReading)
#         .filter(WaterReading.station_id == station_id)
#         .order_by(WaterReading.year.asc())
#         .limit(limit)
#         .all()
#     )


# def get_all_stations_summary(db: Session):
#     stations = db.query(WaterReading.station_id).distinct().all()
#     summaries = []
#     for (station_id,) in stations:
#         latest = (
#             db.query(WaterReading)
#             .filter(WaterReading.station_id == station_id)
#             .order_by(WaterReading.year.desc())
#             .first()
#         )
#         count = (
#             db.query(func.count(WaterReading.id))
#             .filter(WaterReading.station_id == station_id)
#             .scalar()
#         )
#         summaries.append({
#             "station_id": station_id,
#             "latest_year": latest.year if latest else None,
#             "latest_prediction": latest.predicted_source if latest else None,
#             "total_readings": count,
#         })
#     return summaries


# def get_history(db: Session, station_id: str = None, limit: int = 200):
#     query = db.query(WaterReading)
#     if station_id:
#         query = query.filter(WaterReading.station_id == station_id)
#     return query.order_by(WaterReading.year.desc()).limit(limit).all()


from sqlalchemy.orm import Session
from sqlalchemy import func

from app.models.db_models import WaterReading, StationStatus


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


# def get_all_stations_summary(db: Session):
#     stations = db.query(WaterReading.station_id).distinct().all()
#     summaries = []
#     for (station_id,) in stations:
#         latest = (
#             db.query(WaterReading)
#             .filter(WaterReading.station_id == station_id)
#             .order_by(WaterReading.year.desc())
#             .first()
#         )
#         count = (
#             db.query(func.count(WaterReading.id))
#             .filter(WaterReading.station_id == station_id)
#             .scalar()
#         )
#         summaries.append({
#             "station_id": station_id,
#             "latest_year": latest.year if latest else None,
#             "latest_prediction": latest.predicted_source if latest else None,
#             "total_readings": count,
#         })
#     return summaries
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
            "station_name": latest.station_name if latest else None,
            "latest_year": latest.year if latest else None,
            "latest_prediction": latest.predicted_source if latest else None,
            "total_readings": count,
            "latitude": latest.latitude if latest else None,
            "longitude": latest.longitude if latest else None,
        })
    return summaries


def get_history(db: Session, station_id: str = None, limit: int = 200):
    query = db.query(WaterReading)
    if station_id:
        query = query.filter(WaterReading.station_id == station_id)
    return query.order_by(WaterReading.year.desc()).limit(limit).all()


def delete_station(db: Session, station_id: str) -> int:
    """Deletes every reading belonging to a station (i.e. removes the lake
    entirely from the dashboard). Returns the number of rows deleted so the
    route can 404 if nothing matched."""
    deleted_count = (
        db.query(WaterReading)
        .filter(WaterReading.station_id == station_id)
        .delete(synchronize_session=False)
    )
    db.commit()
    return deleted_count

def delete_all_stations(db: Session) -> int:
    """Deletes every reading for every station (full reset of the dashboard).
    Returns the number of rows deleted."""
    deleted_count = db.query(WaterReading).delete(synchronize_session=False)
    db.commit()
    return deleted_count

def get_latest_readings(db):
    """One row per station -- its most recent year's reading."""
    subq = (
        db.query(
            WaterReading.station_id,
            func.max(WaterReading.year).label("max_year"),
        )
        .group_by(WaterReading.station_id)
        .subquery()
    )
    return (
        db.query(WaterReading)
        .join(
            subq,
            (WaterReading.station_id == subq.c.station_id)
            & (WaterReading.year == subq.c.max_year),
        )
        .all()
    )


def get_station_status(db, station_id: str):
    return db.query(StationStatus).filter(
        StationStatus.station_id == station_id
    ).first()


def upsert_station_status(db, station_id: str, status: str, note: str | None = None):
    obj = get_station_status(db, station_id)
    if obj:
        obj.status = status
        if note is not None:
            obj.note = note
    else:
        obj = StationStatus(station_id=station_id, status=status, note=note)
        db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

def get_reading_by_station_and_year(db: Session, station_id: str, year: int):
    return (
        db.query(WaterReading)
        .filter(WaterReading.station_id == station_id, WaterReading.year == year)
        .first()
    )


def update_reading(db: Session, reading: WaterReading, reading_data: dict) -> WaterReading:
    for key, value in reading_data.items():
        setattr(reading, key, value)
    db.commit()
    db.refresh(reading)
    return reading