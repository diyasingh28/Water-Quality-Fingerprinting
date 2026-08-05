import React from "react";
import StationList from "../components/StationList";
import StationMap from "../components/StationMap";
import UploadPanel from "../components/UploadPanel";
import { useStations } from "../hooks/useStationData";

export default function Dashboard() {
  const { stations, loading, error, refresh } = useStations();

  return (
    <div className="dashboard-page">
      <section className="upload-section">
        <UploadPanel onUploaded={refresh} />
      </section>

      {loading && <p>Loading stations...</p>}
      {error && <p className="status-error">Error: {error}</p>}

      {!loading && !error && (
        <>
          <section>
            <h2>Monitoring Stations</h2>
            <StationMap stations={stations} />
          </section>
          <section>
            <StationList stations={stations} />
          </section>
        </>
      )}
    </div>
  );
}
