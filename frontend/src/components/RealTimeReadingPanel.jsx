import React, { useState } from "react";
import { predictSample } from "../services/api";

const LAB_SOURCE_LABELS = {
  provided: { text: "Lab values provided directly", tone: "success" },
  fallback_from_last_lab_test: { text: "Lab values reused from last known test for this station", tone: "warn" },
  no_lab_data_available: { text: "No lab data found for this station — BOD/coliform defaulted to 0. Upload a lab reading first for accurate results.", tone: "error" },
};

const initialForm = {
  station_id: "",
  year: new Date().getFullYear(),
  ph: "",
  conductivity: "",
  dissolved_oxygen: "",
  nitrate: "",
  temperature: "",
};

export default function RealTimeReadingPanel({ onPredicted }) {
  const [form, setForm] = useState(initialForm);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleChange = (field) => (e) => {
    setForm({ ...form, [field]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const sample = {
        station_id: form.station_id,
        year: parseInt(form.year, 10),
        ph_min: parseFloat(form.ph), ph_max: parseFloat(form.ph),
        conductivity_min: parseFloat(form.conductivity), conductivity_max: parseFloat(form.conductivity),
        dissolved_oxygen_min: parseFloat(form.dissolved_oxygen), dissolved_oxygen_max: parseFloat(form.dissolved_oxygen),
        nitrate_min: parseFloat(form.nitrate), nitrate_max: parseFloat(form.nitrate),
        temperature_min: parseFloat(form.temperature), temperature_max: parseFloat(form.temperature),
        // BOD / fecal / total coliform deliberately omitted -- backend
        // falls back to this station's last known lab test automatically.
      };
      const prediction = await predictSample(sample);
      setResult(prediction);
      if (onPredicted) onPredicted();
    } catch (err) {
      setError(err?.response?.data?.detail || err.message);
    } finally {
      setLoading(false);
    }
  };

  const labInfo = result ? LAB_SOURCE_LABELS[result.lab_values_source] : null;

  return (
    <div className="realtime-panel">
      <h3>Simulate Real-Time Sensor Reading</h3>
      <p className="page-note">
        Enter only the 5 live-sensor parameters — BOD, fecal coliform, and
        total coliform are automatically filled in from this station's most
        recent lab-tested reading (upload one first if this is a new station).
      </p>

      <form onSubmit={handleSubmit} className="realtime-form">
        <input
          type="text" placeholder="Station ID" value={form.station_id}
          onChange={handleChange("station_id")} required
        />
        <input
          type="number" placeholder="Year" value={form.year}
          onChange={handleChange("year")} required
        />
        <input
          type="number" step="0.01" placeholder="pH" value={form.ph}
          onChange={handleChange("ph")} required
        />
        <input
          type="number" step="0.1" placeholder="Conductivity (umhos/cm)" value={form.conductivity}
          onChange={handleChange("conductivity")} required
        />
        <input
          type="number" step="0.01" placeholder="Dissolved Oxygen (mg/L)" value={form.dissolved_oxygen}
          onChange={handleChange("dissolved_oxygen")} required
        />
        <input
          type="number" step="0.01" placeholder="Nitrate (mg/L)" value={form.nitrate}
          onChange={handleChange("nitrate")} required
        />
        <input
          type="number" step="0.1" placeholder="Temperature (C)" value={form.temperature}
          onChange={handleChange("temperature")} required
        />
        <button type="submit" disabled={loading}>
          {loading ? "Predicting..." : "Get Real-Time Prediction"}
        </button>
      </form>

      {error && <p className="status-error">Error: {error}</p>}

      {result && (
        <div className="realtime-result">
          <p><strong>Predicted source:</strong> {result.predicted_source}</p>
          <p><strong>Confidence:</strong> {Math.round(result.confidence * 100)}%</p>
          {labInfo && (
            <p className={`lab-source-note lab-source-${labInfo.tone}`}>{labInfo.text}</p>
          )}
        </div>
      )}
    </div>
  );
}
