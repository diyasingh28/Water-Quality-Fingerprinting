from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.core.parameters import AVAILABLE_PARAMETERS


class WaterSampleInput(BaseModel):
    """
    One station reading. Live-sensor parameters (pH, conductivity,
    dissolved oxygen, nitrate, temperature) are required -- these can
    come from a real-time ESP32 node. Lab-only parameters (BOD, fecal
    coliform, total coliform) are OPTIONAL: if omitted, the backend
    automatically falls back to the station's most recent stored lab
    reading (see routes_predict.py). This supports a hybrid real-time +
    periodic-lab-test monitoring design, since BOD/coliform require lab
    incubation and cannot be sensor-measured in real time.
    """
    station_id: str
    year: int

    # Live-sensor parameters -- required
    ph_min: float
    ph_max: float
    dissolved_oxygen_min: float
    dissolved_oxygen_max: float
    conductivity_min: float
    conductivity_max: float
    nitrate_min: float
    nitrate_max: float
    temperature_min: float
    temperature_max: float

    # Lab-only parameters -- optional, fall back to last known lab value
    bod_min: Optional[float] = None
    bod_max: Optional[float] = None
    fecal_coliform_min: Optional[float] = None
    fecal_coliform_max: Optional[float] = None
    total_coliform_min: Optional[float] = None
    total_coliform_max: Optional[float] = None


class PredictionResponse(BaseModel):
    station_id: str
    year: int
    predicted_source: str
    confidence: float
    lab_values_source: str  # "provided" | "fallback_from_last_lab_test" | "no_lab_data_available"


class ShapFeatureContribution(BaseModel):
    feature: str
    shap_value: float
    description: str


class ExplanationResponse(BaseModel):
    station_id: str
    predicted_source: str
    narrative: str
    top_features: list[ShapFeatureContribution]


class StationSummary(BaseModel):
    station_id: str
    latest_year: Optional[int] = None
    latest_prediction: Optional[str] = None
    latest_source_type: Optional[str] = None  # "dataset" | "iot"
    total_readings: int


class HistoryRecord(BaseModel):
    station_id: str
    year: int
    predicted_source: str
    confidence: float
    source_type: Optional[str] = None  # "dataset" | "iot"

    ph_min: Optional[float] = None
    ph_max: Optional[float] = None
    dissolved_oxygen_min: Optional[float] = None
    dissolved_oxygen_max: Optional[float] = None
    bod_min: Optional[float] = None
    bod_max: Optional[float] = None
    conductivity_min: Optional[float] = None
    conductivity_max: Optional[float] = None
    nitrate_min: Optional[float] = None
    nitrate_max: Optional[float] = None
    fecal_coliform_min: Optional[float] = None
    fecal_coliform_max: Optional[float] = None
    total_coliform_min: Optional[float] = None
    total_coliform_max: Optional[float] = None
    temperature_min: Optional[float] = None
    temperature_max: Optional[float] = None


class UploadResponse(BaseModel):
    rows_processed: int
    predictions_generated: int
    message: str
