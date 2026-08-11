// import React from "react";

// /**
//  * Basic placeholder map view. For the full version, swap this out for
//  * react-leaflet or Google Maps (npm install react-leaflet leaflet) and
//  * plot actual station lat/lng — CPCB/TNPCB datasets usually include
//  * coordinates per monitoring station.
//  */
// export default function StationMap({ stations }) {
//   return (
//     <div className="station-map-placeholder">
//       <p className="map-note">
//         Map view placeholder — integrate react-leaflet with station lat/lng
//         from the dataset for the full version.
//       </p>
//       <div className="map-grid">
//         {stations.map((s) => (
//           <div key={s.station_id} className="map-pin">
//             📍 {s.station_id}
//           </div>
//         ))}
//       </div>
//     </div>
//   );
// }


import React from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import { Link } from "react-router-dom";
import L from "leaflet";
import "leaflet/dist/leaflet.css";


delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: require("leaflet/dist/images/marker-icon-2x.png"),
  iconUrl: require("leaflet/dist/images/marker-icon.png"),
  shadowUrl: require("leaflet/dist/images/marker-shadow.png"),
});

export default function StationMap({ stations }) {
  const withCoords = stations.filter((s) => s.latitude && s.longitude);

  if (withCoords.length === 0) {
    return <p className="empty-state">No station coordinates available yet.</p>;
  }

  const center = [withCoords[0].latitude, withCoords[0].longitude];

  return (
    <MapContainer center={center} zoom={5} style={{ height: "420px", borderRadius: "10px" }}>
      <TileLayer
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        attribution='&copy; OpenStreetMap contributors'
      />
      {withCoords.map((s) => (
        <Marker key={s.station_id} position={[s.latitude, s.longitude]}>
          <Popup>
            <strong>{s.station_name ||s.station_id}</strong><br />
            {s.latest_prediction || "No prediction yet"}<br />
            <Link to={`/stations/${encodeURIComponent(s.station_id)}`}>View details</Link>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}