"""
Abstract base class for all data sources.

Every ingestion source (CPCB CSV loader, TN PCB loader, and later the
ESP32/LoRa live sensor feed) must implement this same interface. This is
the key seam that lets Phase 2 swap in live IoT data without touching
preprocessing, feature engineering, models, or the API layer.
"""

from abc import ABC, abstractmethod
import pandas as pd

from ..utils.parameter_config import AVAILABLE_PARAMETERS


class BaseWaterQualitySource(ABC):
    """Common contract for any water-quality data source."""

    #: Canonical columns every source must eventually produce.
    #: Pulled from parameter_config.AVAILABLE_PARAMETERS — the single
    #: source of truth for which parameters this project actually has
    #: real data for. Subclasses (e.g. NWMPLakeSource) may override this
    #: if their real schema differs (e.g. min/max columns instead of
    #: single values).
    REQUIRED_COLUMNS = ["station_id"] + AVAILABLE_PARAMETERS

    @abstractmethod
    def fetch(self) -> pd.DataFrame:
        """Return raw data as a DataFrame with (at least) REQUIRED_COLUMNS."""
        raise NotImplementedError

    def validate(self, df: pd.DataFrame) -> pd.DataFrame:
        """Basic contract check — ensures downstream modules never break."""
        missing = [c for c in self.REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(
                f"{self.__class__.__name__} is missing required columns: {missing}"
            )
        return df
