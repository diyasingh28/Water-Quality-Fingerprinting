// import axios from "axios";

// const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

// const api = axios.create({
//   baseURL: API_BASE_URL,
//   headers: { "Content-Type": "application/json" },
// });

// export const getStations = () => api.get("/stations").then((res) => res.data);

// export const getHistory = (stationId, limit = 200) =>
//   api
//     .get("/history", { params: { station_id: stationId, limit } })
//     .then((res) => res.data);

// export const predictSample = (sample) =>
//   api.post("/predict", sample).then((res) => res.data);

// export const explainSample = (sample) =>
//   api.post("/explain", sample).then((res) => res.data);

// export const uploadCsv = (file) => {
//   const formData = new FormData();
//   formData.append("file", file);
//   return api
//     .post("/upload", formData, {
//       headers: { "Content-Type": "multipart/form-data" },
//     })
//     .then((res) => res.data);
// };

// export default api;

import axios from "axios";

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || "http://localhost:8000";

const api = axios.create({
  baseURL: API_BASE_URL,
  headers: { "Content-Type": "application/json" },
});

export const getStations = () => api.get("/stations").then((res) => res.data);

export const getHistory = (stationId, limit = 200) =>
  api
    .get("/history", { params: { station_id: stationId, limit } })
    .then((res) => res.data);

export const predictSample = (sample) =>
  api.post("/predict", sample).then((res) => res.data);

export const explainSample = (sample) =>
  api.post("/explain", sample).then((res) => res.data);

export const deleteStation = (stationId) =>
  api.delete(`/stations/${encodeURIComponent(stationId)}`).then((res) => res.data);

export const deleteAllStations = () =>
  api.delete("/stations").then((res) => res.data);

export const uploadCsv = (file) => {
  const formData = new FormData();
  formData.append("file", file);
  return api
    .post("/upload", formData, {
      headers: { "Content-Type": "multipart/form-data" },
    })
    .then((res) => res.data);
};

export default api;