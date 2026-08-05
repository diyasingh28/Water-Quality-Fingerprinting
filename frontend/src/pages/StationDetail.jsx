import React, { useState } from "react";
import { useParams, Link } from "react-router-dom";
import PredictionCard from "../components/PredictionCard";
import ShapChart from "../components/ShapChart";
import TrendChart from "../components/TrendChart";
import { useStationHistory } from "../hooks/useStationData";
import { explainSample } from "../services/api";

export default function StationDetail() {
  const { stationId } = useParams();
  const { history, loading, error } = useStationHistory(stationId);
  const [explanation, setExplanation] = useState(null);
  const [explaining, setExplaining] = useState(false);
  const [explainError, setExplainError] = useState(null);

  // history is ordered newest-first (see routes_history.py), so [0] is
  // the latest real reading for this station -- no more dummy values.
  const latest = history && history.length > 0 ? history[0] : null;

  const handleExplainLatest = async () => {
    if (!latest) return;
    setExplaining(true);
    setExplainError(null);
    try {
      const result = await explainSample({
        station_id: latest.station_id,
        year: latest.year,
        ph_min: latest.ph_min, ph_max: latest.ph_max,
        dissolved_oxygen_min: latest.dissolved_oxygen_min, dissolved_oxygen_max: latest.dissolved_oxygen_max,
        bod_min: latest.bod_min, bod_max: latest.bod_max,
        conductivity_min: latest.conductivity_min, conductivity_max: latest.conductivity_max,
        nitrate_min: latest.nitrate_min, nitrate_max: latest.nitrate_max,
        fecal_coliform_min: latest.fecal_coliform_min, fecal_coliform_max: latest.fecal_coliform_max,
        total_coliform_min: latest.total_coliform_min, total_coliform_max: latest.total_coliform_max,
        temperature_min: latest.temperature_min, temperature_max: latest.temperature_max,
      });
      setExplanation(result);
    } catch (err) {
      const detail = err?.response?.data?.detail || err.message;
      setExplainError(detail);
      console.error(err);
    } finally {
      setExplaining(false);
    }
  };

  return (
    <div className="station-detail-page">
      <Link to="/" className="back-link">&larr; Back to Dashboard</Link>
      <h2>Station: {stationId}</h2>

      {loading && <p>Loading history...</p>}
      {error && <p className="status-error">Error: {error}</p>}

      {latest && <PredictionCard prediction={latest} />}

      <button onClick={handleExplainLatest} disabled={explaining || !latest}>
        {explaining ? "Explaining..." : "Explain Latest Prediction"}
      </button>

      {explainError && <p className="status-error">Error: {explainError}</p>}

      {explanation && (
        <ShapChart topFeatures={explanation.top_features} narrative={explanation.narrative} />
      )}

      <TrendChart history={history} />
    </div>
  );
}
