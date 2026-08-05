import React from "react";
import { Link } from "react-router-dom";

export default function StationList({ stations }) {
  if (!stations || stations.length === 0) {
    return <p className="empty-state">No stations yet — upload data or run a prediction to get started.</p>;
  }

  return (
    <div className="station-list">
      {stations.map((s) => (
        <Link to={`/stations/${s.station_id}`} key={s.station_id} className="station-card">
          <h3>{s.station_id}</h3>
          <p className="station-source">{s.latest_prediction || "No prediction yet"}</p>
          <p className="station-meta">
            {s.total_readings} readings
            {s.latest_year ? ` · latest year: ${s.latest_year}` : ""}
          </p>
        </Link>
      ))}
    </div>
  );
}
