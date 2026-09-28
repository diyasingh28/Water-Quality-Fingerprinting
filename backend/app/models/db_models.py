# from sqlalchemy import Column, Integer, String, Float
# from app.db.database import Base
# from app.core.parameters import AVAILABLE_PARAMETERS


# class WaterReading(Base):
#     """
#     One station-year summary reading, matching the real CPCB NWMP lake
#     dataset: each parameter is a Min/Max range across the year, not a
#     single point-in-time value.
#     """
#     __tablename__ = "water_readings"

#     id = Column(Integer, primary_key=True, index=True)
#     station_id = Column(String, index=True, nullable=False)
#     year = Column(Integer, index=True, nullable=False)

#     predicted_source = Column(String, nullable=True)
#     confidence = Column(Float, nullable=True)

#     # Phase 2: mark whether this came from the static dataset or a live sensor
#     source_type = Column(String, default="dataset")  # "dataset" | "iot"


# # Dynamically attach {param}_min / {param}_max columns for each of the 8
# # real available parameters, so this stays in sync with
# # app/core/parameters.py without hand-listing every column twice.
# for _param in AVAILABLE_PARAMETERS:
#     setattr(WaterReading, f"{_param}_min", Column(Float, nullable=True))
#     setattr(WaterReading, f"{_param}_max", Column(Float, nullable=True))


from sqlalchemy import Column, DateTime, Integer, String, Float, Text, Boolean
from app.db.database import Base
from app.core.parameters import AVAILABLE_PARAMETERS
from datetime import datetime


class WaterReading(Base):
    """
    One station-year summary reading, matching the real CPCB NWMP lake
    dataset: each parameter is a Min/Max range across the year, not a
    single point-in-time value.
    """
    __tablename__ = "water_readings"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String, index=True, nullable=False)
    station_name = Column(String, nullable=True)
    year = Column(Integer, index=True, nullable=False)

    predicted_source = Column(String, nullable=True)
    confidence = Column(Float, nullable=True)

    # Phase 2: mark whether this came from the static dataset or a live sensor
    source_type = Column(String, default="dataset")  # "dataset" | "iot"

    # Station coordinates (for map view) — same for every reading of a given
    # station, but stored per-row since there's no separate stations table
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)

    is_anomaly = Column(Boolean, default=False)
    anomaly_details = Column(Text, nullable=True)  # JSON string


# Dynamically attach {param}_min / {param}_max columns for each of the 8
# real available parameters, so this stays in sync with
# app/core/parameters.py without hand-listing every column twice.
for _param in AVAILABLE_PARAMETERS:
    setattr(WaterReading, f"{_param}_min", Column(Float, nullable=True))
    setattr(WaterReading, f"{_param}_max", Column(Float, nullable=True))


class StationStatus(Base):
    __tablename__ = "station_status"

    station_id = Column(String, primary_key=True, index=True)
    status = Column(String, default="unaddressed", nullable=False)  # unaddressed | planned | completed
    note = Column(String, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)