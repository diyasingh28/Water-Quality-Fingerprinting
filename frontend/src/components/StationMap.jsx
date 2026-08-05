import React from "react";

/**
 * Basic placeholder map view. For the full version, swap this out for
 * react-leaflet or Google Maps (npm install react-leaflet leaflet) and
 * plot actual station lat/lng — CPCB/TNPCB datasets usually include
 * coordinates per monitoring station.
 */
export default function StationMap({ stations }) {
  return (
    <div className="station-map-placeholder">
      <p className="map-note">
        Map view placeholder — integrate react-leaflet with station lat/lng
        from the dataset for the full version.
      </p>
      <div className="map-grid">
        {stations.map((s) => (
          <div key={s.station_id} className="map-pin">
            📍 {s.station_id}
          </div>
        ))}
      </div>
    </div>
  );
}
