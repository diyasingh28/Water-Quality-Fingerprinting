import React from "react";

export default function TreatmentRecommendations({ recommendations }) {
  if (!recommendations) return null;

  const { predicted_class, general_recommendations, targeted_recommendations } = recommendations;

return (
    <div className="treatment-card">
    <h3>Suggested Treatment Approach</h3>
    <p className="treatment-subtitle">
        {recommendations.station_name && <>For <strong>{recommendations.station_name}</strong> — </>}
        classified as <strong>{predicted_class.replace(/_/g, " ")}</strong>
    </p>

      {targeted_recommendations && targeted_recommendations.length > 0 && (
        <div className="treatment-targeted">
          <h4>Priority actions (based on this sample's key drivers)</h4>
          <ul>
            {targeted_recommendations.map((tip, i) => (
              <li key={i} className="treatment-targeted-item">{tip}</li>
            ))}
          </ul>
        </div>
      )}

      <div className="treatment-general">
        <h4>General treatment options for this category</h4>
        <ul>
          {general_recommendations.map((rec, i) => (
            <li key={i}>{rec}</li>
          ))}
        </ul>
      </div>
    </div>
  );
}