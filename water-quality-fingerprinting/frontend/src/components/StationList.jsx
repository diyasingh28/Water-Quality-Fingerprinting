import React, { useState } from "react";
import { Link } from "react-router-dom";
import { deleteStation } from "../services/api";

function SourceBadge({ sourceType }) {
  if (!sourceType) return null;
  const isLive = sourceType === "iot";
  return (
    <span className={`source-badge ${isLive ? "source-badge-live" : "source-badge-dataset"}`}>
      {isLive ? "Live Sensor" : "Lab / Dataset"}
    </span>
  );
}

export default function StationList({ stations, onDeleted }) {
  const [deletingId, setDeletingId] = useState(null);

  if (!stations || stations.length === 0) {
    return <p className="empty-state">No stations yet — upload data or run a prediction to get started.</p>;
  }

  const handleDelete = async (e, stationId) => {
    e.preventDefault(); // don't navigate into the station link
    e.stopPropagation();

    const confirmed = window.confirm(
      `Delete all data for "${stationId}"? This cannot be undone.`
    );
    if (!confirmed) return;

    setDeletingId(stationId);
    try {
      await deleteStation(stationId);
      if (onDeleted) onDeleted();
    } catch (err) {
      alert(`Failed to delete: ${err?.response?.data?.detail || err.message}`);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="station-list">
      {stations.map((s) => (
        <div key={s.station_id} className="station-card-wrapper">
          <Link to={`/stations/${encodeURIComponent(s.station_id)}`} className="station-card">
            <div className="station-card-top">
              <h3>{s.station_id}</h3>
              <SourceBadge sourceType={s.latest_source_type} />
            </div>
            <p className="station-source">{s.latest_prediction || "No prediction yet"}</p>
            <p className="station-meta">
              {s.total_readings} readings
              {s.latest_year ? ` · latest year: ${s.latest_year}` : ""}
            </p>
          </Link>
          <button
            className="delete-station-btn"
            onClick={(e) => handleDelete(e, s.station_id)}
            disabled={deletingId === s.station_id}
            title={`Delete ${s.station_id}`}
          >
            {deletingId === s.station_id ? "Deleting..." : "Delete"}
          </button>
        </div>
      ))}
    </div>
  );
}
