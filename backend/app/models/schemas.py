from pydantic import BaseModel
from typing import Optional
from datetime import datetime

from app.core.parameters import AVAILABLE_PARAMETERS


def _build_min_max_fields():
    """Documents the expected shape: {param}_min and {param}_max for each
    of the 8 real available parameters (see app/core/parameters.py)."""
    return {f"{p}_min": float for p in AVAILABLE_PARAMETERS} | {
        f"{p}_max": float for p in AVAILABLE_PARAMETERS
    }


class WaterSampleInput(BaseModel):
    """
    One station-year summary, matching the real CPCB NWMP lake dataset
    structure: each parameter is reported as a Min/Max range across the
    year, not a single point-in-time reading.
    """
    station_id: str
    year: int

    ph_min: float
    ph_max: float
    dissolved_oxygen_min: float
    dissolved_oxygen_max: float
    bod_min: float
    bod_max: float
    conductivity_min: float
    conductivity_max: float
    nitrate_min: float
    nitrate_max: float
    fecal_coliform_min: float
    fecal_coliform_max: float
    total_coliform_min: float
    total_coliform_max: float
    temperature_min: float
    temperature_max: float


class PredictionResponse(BaseModel):
    station_id: str
    year: int
    predicted_source: str
    confidence: float


class ShapFeatureContribution(BaseModel):
    feature: str
    shap_value: float
    description: str


class WaterfallData(BaseModel):
    base_value: float
    final_value: float
    predicted_class: str
    contributions: list[ShapFeatureContribution]


class TreatmentRecommendations(BaseModel):
    predicted_class: str
    general_recommendations: list[str]
    targeted_recommendations: list[str]
    station_name: str | None = None

class ExplanationResponse(BaseModel):
    station_id: str
    predicted_source: str
    narrative: str
    top_features: list[ShapFeatureContribution]
    waterfall: WaterfallData
    sample_values: dict[str, float]
    category_ranges: dict | None = None
    recommendations: TreatmentRecommendations

# class ExplanationResponse(BaseModel):
#     station_id: str
#     predicted_source: str
#     narrative: str
#     top_features: list[ShapFeatureContribution]


class StationSummary(BaseModel):
    station_id: str
    station_name: Optional[str] = None
    latest_year: Optional[int] = None
    latest_prediction: Optional[str] = None
    total_readings: int
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class HistoryRecord(BaseModel):
    station_id: str
    station_name: Optional[str] = None
    year: int
    predicted_source: str
    confidence: float
    is_anomaly: bool = False
    anomaly_details: list[dict] = []

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
