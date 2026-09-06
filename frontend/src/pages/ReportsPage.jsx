import React, { useMemo } from "react";
import { useStations } from "../hooks/useStationData";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

function summarize(stations) {
  const counts = {};
  let totalReadings = 0;
  for (const s of stations) {
    const cat = s.latest_prediction || "unclassified";
    counts[cat] = (counts[cat] || 0) + 1;
    totalReadings += s.total_readings || 0;
  }
  return { counts, totalReadings, totalStations: stations.length };
}

export default function ReportsPage() {
  const { stations, loading } = useStations();
  const summary = useMemo(() => summarize(stations || []), [stations]);

  return (
    <div className="reports-page">
      <h2>Reports</h2>

      {!loading && (
        <div className="reports-summary">
          <div className="summary-stat">
            <span className="summary-number">{summary.totalStations}</span>
            <span className="summary-label">Stations</span>
          </div>
          <div className="summary-stat">
            <span className="summary-number">{summary.totalReadings}</span>
            <span className="summary-label">Total Readings</span>
          </div>
          {Object.entries(summary.counts).map(([cat, count]) => (
            <div className="summary-stat" key={cat}>
              <span className="summary-number">{count}</span>
              <span className="summary-label">{cat.replace(/_/g, " ")}</span>
            </div>
          ))}
        </div>
      )}

      {loading ? (
        <p>Loading stations...</p>
      ) : (
        <table className="reports-table">
          <thead>
            <tr>
              <th>Station</th>
              <th>Latest Prediction</th>
              <th>Readings</th>
              <th>Download</th>
            </tr>
          </thead>
          <tbody>
            {stations.map((s) => (
              <tr key={s.station_id}>
                <td>{s.station_name || s.station_id}</td>
                <td className={`prediction-tag prediction-${s.latest_prediction}`}>
                  {s.latest_prediction || "—"}
                </td>
                <td>{s.total_readings}</td>
                <td className="download-cell">
                  <a href={`${API_BASE}/reports/${s.station_id}/csv`} className="download-link">CSV</a>
                  <a href={`${API_BASE}/reports/${s.station_id}/pdf`} className="download-link">PDF</a>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      )}
    </div>
  );
}
