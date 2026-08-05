import React from "react";
import {
  LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
} from "recharts";

export default function TrendChart({ history }) {
  if (!history || history.length === 0) {
    return <p className="empty-state">No historical data yet for this station.</p>;
  }

  const data = [...history]
    .reverse()
    .map((h) => ({
      year: h.year,
      confidence: Math.round((h.confidence || 0) * 100),
    }));

  return (
    <div className="trend-chart">
      <h3>Prediction Confidence Over Time</h3>
      <ResponsiveContainer width="100%" height={280}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="year" tick={{ fontSize: 11 }} />
          <YAxis domain={[0, 100]} />
          <Tooltip />
          <Legend />
          <Line type="monotone" dataKey="confidence" stroke="#2563eb" strokeWidth={2} dot={false} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
