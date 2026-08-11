// import { useState, useEffect, useCallback } from "react";
// import { getStations, getHistory } from "../services/api";

// export function useStations() {
//   const [stations, setStations] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);

//   const refresh = useCallback(() => {
//     setLoading(true);
//     getStations()
//       .then(setStations)
//       .catch((err) => setError(err.message))
//       .finally(() => setLoading(false));
//   }, []);

//   useEffect(() => {
//     refresh();
//   }, [refresh]);

//   return { stations, loading, error, refresh };
// }

// export function useStationHistory(stationId) {
//   const [history, setHistory] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);

//   useEffect(() => {
//     if (!stationId) return;
//     setLoading(true);
//     getHistory(stationId)
//       .then(setHistory)
//       .catch((err) => setError(err.message))
//       .finally(() => setLoading(false));
//   }, [stationId]);

//   return { history, loading, error };
// }

// import { useState, useEffect, useCallback } from "react";
// import { getStations, getHistory } from "../services/api";

// export function useStations() {
//   const [stations, setStations] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);

//   const refresh = useCallback(() => {
//     setLoading(true);
//     getStations()
//       .then(setStations)
//       .catch((err) => setError(err.message))
//       .finally(() => setLoading(false));
//   }, []);

//   useEffect(() => {
//     refresh();
//   }, [refresh]);

//   const removeStationLocally = useCallback((stationId) => {
//     setStations((prev) => prev.filter((s) => s.station_id !== stationId));
//   }, []);

//   return { stations, loading, error, refresh, removeStationLocally };
// }

// export function useStationHistory(stationId) {
//   const [history, setHistory] = useState([]);
//   const [loading, setLoading] = useState(true);
//   const [error, setError] = useState(null);

//   useEffect(() => {
//     if (!stationId) return;
//     setLoading(true);
//     getHistory(stationId)
//       .then(setHistory)
//       .catch((err) => setError(err.message))
//       .finally(() => setLoading(false));
//   }, [stationId]);

//   return { history, loading, error };
// }

import { useState, useEffect, useCallback } from "react";
import { getStations, getHistory, deleteAllStations } from "../services/api";

export function useStations() {
  const [stations, setStations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const refresh = useCallback(() => {
    setLoading(true);
    getStations()
      .then(setStations)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  useEffect(() => {
    refresh();
  }, [refresh]);

  const removeStationLocally = useCallback((stationId) => {
    setStations((prev) => prev.filter((s) => s.station_id !== stationId));
  }, []);

  const resetAll = useCallback(async () => {
    await deleteAllStations();
    setStations([]);
  }, []);

  return { stations, loading, error, refresh, removeStationLocally, resetAll };
}

export function useStationHistory(stationId) {
  const [history, setHistory] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!stationId) return;
    setLoading(true);
    getHistory(stationId)
      .then(setHistory)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [stationId]);

  return { history, loading, error };
}