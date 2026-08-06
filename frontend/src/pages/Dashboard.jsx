// import React from "react";
// import StationList from "../components/StationList";
// import StationMap from "../components/StationMap";
// import UploadPanel from "../components/UploadPanel";
// import { useStations } from "../hooks/useStationData";

// export default function Dashboard() {
//   const { stations, loading, error, refresh } = useStations();

//   return (
//     <div className="dashboard-page">
//       <section className="upload-section">
//         <UploadPanel onUploaded={refresh} />
//       </section>

//       {loading && <p>Loading stations...</p>}
//       {error && <p className="status-error">Error: {error}</p>}

//       {!loading && !error && (
//         <>
//           <section>
//             <h2>Monitoring Stations</h2>
//             <StationMap stations={stations} />
//           </section>
//           <section>
//             <StationList stations={stations} />
//           </section>
//         </>
//       )}
//     </div>
//   );
// }

import React from "react";
import StationList from "../components/StationList";
import StationMap from "../components/StationMap";
import UploadPanel from "../components/UploadPanel";
import { useStations } from "../hooks/useStationData";

export default function Dashboard() {
  const { stations, loading, error, refresh, removeStationLocally } = useStations();

  const totalReadings = stations.reduce((sum, s) => sum + (s.total_readings || 0), 0);
  const liveCount = stations.filter((s) => s.latest_prediction).length;

  return (
    <div className="dashboard-page">
      <section className="dashboard-hero">
        <div>
          <h2 className="hero-title">Monitoring Overview</h2>
          <p className="hero-subtitle">
            Pollution source attribution across every tracked lake, powered by SHAP-explained predictions.
          </p>
        </div>
        {!loading && !error && (
          <div className="stat-pills">
            <div className="stat-pill">
              <span className="stat-pill-value">{stations.length}</span>
              <span className="stat-pill-label">Lakes tracked</span>
            </div>
            <div className="stat-pill">
              <span className="stat-pill-value">{totalReadings}</span>
              <span className="stat-pill-label">Total readings</span>
            </div>
            <div className="stat-pill">
              <span className="stat-pill-value">{liveCount}</span>
              <span className="stat-pill-label">With predictions</span>
            </div>
          </div>
        )}
      </section>

      <section className="upload-section">
        <UploadPanel onUploaded={refresh} />
      </section>

      {loading && <p className="loading-state">Loading stations...</p>}
      {error && <p className="status-error">Error: {error}</p>}

      {!loading && !error && (
        <>
          <section>
            <h2 className="section-title">Station Map</h2>
            <StationMap stations={stations} />
          </section>
          <section>
            <div className="section-heading-row">
              <h2 className="section-title">Lakes</h2>
              <span className="section-hint">Tap the trash icon to remove a lake you no longer need to track</span>
            </div>
            <StationList stations={stations} onDeleted={removeStationLocally} />
          </section>
        </>
      )}
    </div>
  );
}