import React from "react";

export default function AnomalyBanner({ reading }) {
  if (!reading || !reading.is_anomaly) return null;

  const details = reading.anomaly_details || [];
  const top = details[0];

  return (
    <div className="anomaly-banner">
      <span className="anomaly-banner-icon">⚡</span>
      <div>
        <strong>Unusual reading detected</strong>
        {top && (
          <p className="anomaly-banner-text">
            {top.parameter.replace(/_/g, " ")} measured at {top.value} is significantly
            different from this station's typical pattern
            (~{top.historical_mean} ± {top.historical_std} over recent years),
            z-score: {top.z_score}.
          </p>
        )}
        {details.length > 1 && (
          <p className="anomaly-banner-more">
            +{details.length - 1} other parameter{details.length - 1 > 1 ? "s" : ""} also flagged.
          </p>
        )}
      </div>
    </div>
  );
}