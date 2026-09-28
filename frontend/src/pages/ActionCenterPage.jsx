import React, { useEffect, useState, useMemo } from "react";
import { Link } from "react-router-dom";

const API_BASE = process.env.REACT_APP_API_BASE || "http://localhost:8000";

const CATEGORY_LABELS = {
  sewage_domestic: "Sewage Domestic",
  industrial: "Industrial",
  agricultural_runoff: "Agricultural Runoff",
  natural_background: "Natural Background",
  unclassified: "Unclassified",
};

export default function ActionCenterPage() {
  const [items, setItems] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAll, setShowAll] = useState(false);
  const [updating, setUpdating] = useState({});

  useEffect(() => {
    fetch(`${API_BASE}/action-center`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to load action center data");
        return res.json();
      })
      .then(setItems)
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, []);

  const handleStatusChange = async (stationId, newStatus) => {
    setUpdating((u) => ({ ...u, [stationId]: true }));
    try {
      const res = await fetch(`${API_BASE}/action-center/${stationId}/status`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ status: newStatus }),
      });
      if (!res.ok) throw new Error("Failed to update status");
      const updated = await res.json();
      setItems((prev) => prev.map((i) => (i.station_id === stationId ? updated : i)));
    } catch (err) {
      alert(err.message);
    } finally {
      setUpdating((u) => ({ ...u, [stationId]: false }));
    }
  };

  const { urgent, planned, completed, others } = useMemo(() => {
    const urgent = [];
    const planned = [];
    const completed = [];
    const others = [];
    for (const item of items) {
      if (!item.actionable) others.push(item);
      else if (item.status === "completed") completed.push(item);
      else if (item.status === "planned") planned.push(item);
      else urgent.push(item);
    }
    urgent.sort((a, b) => b.severity_score - a.severity_score);
    planned.sort((a, b) => b.severity_score - a.severity_score);
    return { urgent, planned, completed, others };
  }, [items]);

  if (loading) {
    return (
      <div className="action-center-page">
        <p>Loading action center...</p>
      </div>
    );
  }
  if (error) {
    return (
      <div className="action-center-page">
        <p className="status-error">Error: {error}</p>
      </div>
    );
  }

  return (
    <div className="action-center-page">
      <div className="action-center-header">
        <h2>Action Center</h2>
        <p className="page-subtitle">
          Lakes prioritized by how urgently they need treatment attention.
        </p>
      </div>

      <div className="action-center-stats">
        <div className="ac-stat ac-stat-urgent">
          <span className="ac-stat-number">{urgent.length}</span>
          <span className="ac-stat-label">Needs Attention</span>
        </div>
        <div className="ac-stat ac-stat-planned">
          <span className="ac-stat-number">{planned.length}</span>
          <span className="ac-stat-label">Planned</span>
        </div>
        <div className="ac-stat ac-stat-completed">
          <span className="ac-stat-number">{completed.length}</span>
          <span className="ac-stat-label">Completed</span>
        </div>
      </div>

      <section className="action-section">
        <h3>Needs Attention</h3>
        {urgent.length === 0 ? (
          <p className="empty-state">No unaddressed urgent cases right now.</p>
        ) : (
          <div className="action-card-list">
            {urgent.map((item) => (
              <ActionCard
                key={item.station_id}
                item={item}
                onStatusChange={handleStatusChange}
                updating={updating[item.station_id]}
              />
            ))}
          </div>
        )}
      </section>

      {planned.length > 0 && (
        <section className="action-section">
          <h3>Planned</h3>
          <div className="action-card-list">
            {planned.map((item) => (
              <ActionCard
                key={item.station_id}
                item={item}
                onStatusChange={handleStatusChange}
                updating={updating[item.station_id]}
              />
            ))}
          </div>
        </section>
      )}

      {completed.length > 0 && (
        <CollapsibleSection title={`Recently Addressed (${completed.length})`}>
          <div className="action-card-list">
            {completed.map((item) => (
              <ActionCard
                key={item.station_id}
                item={item}
                onStatusChange={handleStatusChange}
                updating={updating[item.station_id]}
              />
            ))}
          </div>
        </CollapsibleSection>
      )}

      <div className="show-all-toggle">
        <label>
          <input
            type="checkbox"
            checked={showAll}
            onChange={(e) => setShowAll(e.target.checked)}
          />
          Show all stations (including natural background / unclassified)
        </label>
      </div>

      {showAll && others.length > 0 && (
        <section className="action-section">
          <h3>Other Stations</h3>
          <div className="action-card-list">
            {others.map((item) => (
              <ActionCard key={item.station_id} item={item} readOnly />
            ))}
          </div>
        </section>
      )}
    </div>
  );
}

function CollapsibleSection({ title, children }) {
  const [open, setOpen] = useState(false);
  return (
    <section className="action-section collapsible-section">
      <button className="collapsible-toggle" onClick={() => setOpen((v) => !v)}>
        {open ? "\u25be" : "\u25b8"} {title}
      </button>
      {open && children}
    </section>
  );
}

function ActionCard({ item, onStatusChange, updating, readOnly }) {
  const severityClass = `severity-${item.severity_label.toLowerCase()}`;
  return (
    <div className={`action-card ${severityClass}`}>
      <div className="action-card-top">
        <div>
          <Link to={`/stations/${item.station_id}`} className="action-card-title">
            {item.station_name || item.station_id}
          </Link>
          <div className="action-card-meta">
            <span className={`prediction-tag prediction-${item.predicted_source}`}>
              {CATEGORY_LABELS[item.predicted_source] || item.predicted_source}
            </span>
            <span className="action-card-year">Year: {item.year}</span>
          </div>
        </div>
        {item.actionable && (
          <span className={`severity-badge ${severityClass}`}>
            {item.severity_label}
            {item.severity_score > 0 && ` (+${item.severity_score}%)`}
          </span>
        )}
        {item.is_anomaly && (
          <span className="anomaly-badge">⚡ Anomaly</span>
        )}
        {item.anomaly_summary && (
          <p className="anomaly-summary">{item.anomaly_summary}</p>
        )}
      </div>

      {!readOnly && (
        <div className="action-card-status">
          <label>Status:</label>
          <select
            value={item.status}
            disabled={updating}
            onChange={(e) => onStatusChange(item.station_id, e.target.value)}
          >
            <option value="unaddressed">Unaddressed</option>
            <option value="planned">Planned</option>
            <option value="completed">Completed</option>
          </select>
        </div>
      )}
    </div>
  );
}