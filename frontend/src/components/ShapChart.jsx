import React from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell,
} from "recharts";

export default function ShapChart({ topFeatures, narrative }) {
  if (!topFeatures || topFeatures.length === 0) {
    return <p className="empty-state">No explanation available yet.</p>;
  }

  const data = topFeatures.map((f) => ({
    name: f.description || f.feature,
    value: f.shap_value,
  }));

  return (
    <div className="shap-chart">
      <h3>Why this prediction? (SHAP)</h3>
      {narrative && <p className="shap-narrative">{narrative}</p>}
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data} layout="vertical" margin={{ left: 40, right: 20 }}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis type="number" />
          <YAxis type="category" dataKey="name" width={200} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Bar dataKey="value">
            {data.map((entry, index) => (
              <Cell key={index} fill={entry.value > 0 ? "#dc2626" : "#2563eb"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
