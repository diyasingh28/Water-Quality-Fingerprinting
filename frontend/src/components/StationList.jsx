// import React from "react";
// import { Link } from "react-router-dom";

// export default function StationList({ stations }) {
//   if (!stations || stations.length === 0) {
//     return <p className="empty-state">No stations yet — upload data or run a prediction to get started.</p>;
//   }

//   return (
//     <div className="station-list">
//       {stations.map((s) => (
//         <Link to={`/stations/${s.station_id}`} key={s.station_id} className="station-card">
//           <h3>{s.station_id}</h3>
//           <p className="station-source">{s.latest_prediction || "No prediction yet"}</p>
//           <p className="station-meta">
//             {s.total_readings} readings
//             {s.latest_year ? ` · latest year: ${s.latest_year}` : ""}
//           </p>
//         </Link>
//       ))}
//     </div>
//   );
// }

import React, { useState } from "react";
import { Link } from "react-router-dom";
import { deleteStation } from "../services/api";

export default function StationList({ stations, onDeleted }) {
  const [pendingId, setPendingId] = useState(null); // station awaiting confirmation
  const [deletingId, setDeletingId] = useState(null); // station currently being deleted
  const [error, setError] = useState(null);

  if (!stations || stations.length === 0) {
    return <p className="empty-state">No stations yet — upload data or run a prediction to get started.</p>;
  }

  const handleDeleteClick = (e, stationId) => {
    e.preventDefault();
    e.stopPropagation();
    setError(null);
    setPendingId(stationId);
  };

  const handleCancel = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setPendingId(null);
  };

  const handleConfirm = async (e, stationId) => {
    e.preventDefault();
    e.stopPropagation();
    setDeletingId(stationId);
    try {
      await deleteStation(stationId);
      setPendingId(null);
      if (onDeleted) onDeleted(stationId);
    } catch (err) {
      const detail = err?.response?.data?.detail || err.message;
      setError(`Couldn't delete ${stationId}: ${detail}`);
      setPendingId(null);
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="station-list">
      {error && <p className="status-error station-list-error">{error}</p>}
      {stations.map((s) => (
        <Link
          to={`/stations/${s.station_id}`}
          key={s.station_id}
          className={`station-card ${pendingId === s.station_id ? "station-card-confirming" : ""}`}
        >
          <div className="station-card-top">
            <h3>{s.station_id}</h3>
            <button
              type="button"
              className="delete-icon-btn"
              title="Delete this lake"
              aria-label={`Delete ${s.station_id}`}
              onClick={(e) => handleDeleteClick(e, s.station_id)}
              disabled={deletingId === s.station_id}
            >
              🗑
            </button>
          </div>

          <p className="station-source">{s.latest_prediction || "No prediction yet"}</p>
          <p className="station-meta">
            {s.total_readings} readings
            {s.latest_year ? ` · latest year: ${s.latest_year}` : ""}
          </p>

          {pendingId === s.station_id && (
            <div className="delete-confirm-row">
              <span>Remove this lake and all its readings?</span>
              <div className="delete-confirm-actions">
                <button
                  type="button"
                  className="confirm-delete-btn"
                  onClick={(e) => handleConfirm(e, s.station_id)}
                  disabled={deletingId === s.station_id}
                >
                  {deletingId === s.station_id ? "Deleting..." : "Delete"}
                </button>
                <button type="button" className="cancel-delete-btn" onClick={handleCancel}>
                  Cancel
                </button>
              </div>
            </div>
          )}
        </Link>
      ))}
    </div>
  );
}