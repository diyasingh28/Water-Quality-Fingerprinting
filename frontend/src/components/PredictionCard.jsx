import React from "react";

export default function PredictionCard({ prediction }) {
  if (!prediction) return null;

  const confidencePct = Math.round((prediction.confidence || 0) * 100);

  return (
    <div className="prediction-card">
      <h3>Predicted Pollution Source</h3>
      <p className="prediction-source">{prediction.predicted_source}</p>
      <div className="confidence-bar-track">
        <div className="confidence-bar-fill" style={{ width: `${confidencePct}%` }} />
      </div>
      <p className="confidence-label">{confidencePct}% confidence</p>
    </div>
  );
}
