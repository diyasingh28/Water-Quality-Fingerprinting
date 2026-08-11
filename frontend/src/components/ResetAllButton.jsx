import React, { useState } from "react";

export default function ResetAllButton({ onReset }) {
  const [confirming, setConfirming] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState(null);

  const handleReset = async () => {
    setBusy(true);
    setError(null);
    try {
      await onReset();
      setConfirming(false);
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  };

  if (!confirming) {
    return (
      <button
        type="button"
        className="delete-icon-btn reset-all-trigger"
        onClick={() => setConfirming(true)}
      >
        Reset All Data
      </button>
    );
  }

  return (
    <div className="delete-confirm-row reset-all-confirm">
      <span>This will permanently delete every lake and reading. Are you sure?</span>
      <div className="delete-confirm-actions">
        <button
          type="button"
          className="confirm-delete-btn"
          onClick={handleReset}
          disabled={busy}
        >
          {busy ? "Deleting..." : "Yes, delete all"}
        </button>
        <button
          type="button"
          className="cancel-delete-btn"
          onClick={() => setConfirming(false)}
          disabled={busy}
        >
          Cancel
        </button>
      </div>
      {error && <p className="status-error">Error: {error}</p>}
    </div>
  );
}