import React from "react";
import { useStations } from "../hooks/useStationData";

export default function ReportsPage() {
  const { stations, loading } = useStations();

  return (
    <div className="reports-page">
      <h2>Reports</h2>
      {/* <p className="page-note">
        Backend report endpoints (PDF/CSV export) are implemented in
        <code> app/services/report_service.py</code> — wire up a
        `/reports/{"{"}station_id{"}"}` route in the backend if you want
        direct download links here.
      </p> */}
      {loading ? (
        <p>Loading stations...</p>
      ) : (
        <ul className="report-list">
          {stations.map((s) => (
            <li key={s.station_id}>{s.station_id} — {s.total_readings} readings</li>
          ))}
        </ul>
      )}
    </div>
  );
}
