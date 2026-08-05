import React, { useState } from "react";
import { uploadCsv } from "../services/api";

export default function UploadPanel({ onUploaded }) {
  const [file, setFile] = useState(null);
  const [status, setStatus] = useState(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) return;
    setLoading(true);
    setStatus(null);
    try {
      const result = await uploadCsv(file);
      setStatus({ type: "success", message: `${result.predictions_generated} predictions generated from ${result.rows_processed} rows.` });
      if (onUploaded) onUploaded();
    } catch (err) {
      const detail = err?.response?.data?.detail || err.message;
      setStatus({ type: "error", message: detail });
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="upload-panel" onSubmit={handleSubmit}>
      <h3>Upload Water Quality CSV</h3>
      <input
        type="file"
        accept=".csv"
        onChange={(e) => setFile(e.target.files[0])}
      />
      <button type="submit" disabled={!file || loading}>
        {loading ? "Processing..." : "Upload & Predict"}
      </button>
      {status && (
        <p className={status.type === "error" ? "status-error" : "status-success"}>
          {status.message}
        </p>
      )}
    </form>
  );
}
