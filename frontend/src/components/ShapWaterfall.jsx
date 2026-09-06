// import React from "react";
// import {
//   BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
//   Cell, ReferenceLine,
// } from "recharts";

// // Long descriptions like "BOD-to-Dissolved-Oxygen ratio (oxygen demand
// // pressure) (multi-year rolling average)" are great in the narrative
// // text, but unreadable as an axis label. Cut at the first parenthetical
// // and truncate as a fallback, keeping the full text for the tooltip.
// function shortenLabel(text, maxLen = 32) {
//   const base = text.split(" (")[0].trim();
//   const source = base.length >= 6 ? base : text;
//   return source.length > maxLen ? source.slice(0, maxLen - 1) + "…" : source;
// }

// function CustomYAxisTick({ x, y, payload }) {
//   const short = shortenLabel(payload.value);
//   return (
//     <g transform={`translate(${x},${y})`}>
//       <text
//         x={0}
//         y={0}
//         dy={4}
//         textAnchor="end"
//         fontSize={12}
//         fill="#334155"
//       >
//         {short}
//         <title>{payload.value}</title>
//       </text>
//     </g>
//   );
// }

// export default function ShapWaterfall({ waterfall, narrative }) {
//   if (!waterfall || !waterfall.contributions || waterfall.contributions.length === 0) {
//     return <p className="empty-state">No explanation available yet.</p>;
//   }

//   const { base_value, final_value, predicted_class, contributions } = waterfall;

//   let cumulative = base_value;
//   const data = contributions.map((c) => {
//     const start = cumulative;
//     cumulative += c.shap_value;
//     const end = cumulative;
//     return {
//       name: c.description || c.feature,
//       spacer: Math.min(start, end),
//       value: Math.abs(end - start),
//       isPositive: c.shap_value >= 0,
//       rawValue: c.shap_value,
//     };
//   });

//   const rowHeight = 42;
//   const chartHeight = Math.max(340, data.length * rowHeight + 60);

//   return (
//     <div className="shap-waterfall-card">
//       <div className="shap-waterfall-header">
//         <h3>Why "{predicted_class}"?</h3>
//         {narrative && <p className="shap-narrative">{narrative}</p>}
//       </div>

//       <div className="shap-waterfall-legend">
//         <span className="legend-item">
//           <span className="legend-swatch increase" /> Pushes toward {predicted_class}
//         </span>
//         <span className="legend-item">
//           <span className="legend-swatch decrease" /> Pushes away
//         </span>
//       </div>

//       <ResponsiveContainer width="100%" height={chartHeight}>
//         <BarChart
//           data={data}
//           layout="vertical"
//           margin={{ top: 24, right: 60, left: 10, bottom: 10 }}
//           barCategoryGap={14}
//         >
//           <CartesianGrid strokeDasharray="3 3" horizontal={false} />
//           <XAxis type="number" tick={{ fontSize: 12 }} />
//           <YAxis
//             type="category"
//             dataKey="name"
//             width={210}
//             tick={<CustomYAxisTick />}
//             interval={0}
//           />
//           <Tooltip
//             formatter={(_val, _name, props) => [
//               `${props.payload.rawValue > 0 ? "+" : ""}${props.payload.rawValue.toFixed(3)}`,
//               "Impact",
//             ]}
//             labelFormatter={(label) => label}
//           />
//           <ReferenceLine
//             x={base_value}
//             stroke="#94a3b8"
//             strokeDasharray="4 4"
//             label={{ value: "Base", position: "top", fontSize: 11, fill: "#64748b", offset: 8 }}
//           />
//           <ReferenceLine
//             x={final_value}
//             stroke="#1e293b"
//             strokeWidth={1.5}
//             label={{ value: "Prediction", position: "top", fontSize: 11, fill: "#1e293b", offset: 8 }}
//           />
//           <Bar dataKey="spacer" stackId="a" fill="transparent" isAnimationActive={false} />
//           <Bar dataKey="value" stackId="a" radius={[3, 3, 3, 3]} barSize={18}>
//             {data.map((entry, index) => (
//               <Cell key={index} fill={entry.isPositive ? "#dc2626" : "#2563eb"} />
//             ))}
//           </Bar>
//         </BarChart>
//       </ResponsiveContainer>

//       <div className="shap-waterfall-footer">
//         <span>Base: <strong>{base_value.toFixed(2)}</strong></span>
//         <span>→</span>
//         <span>Final: <strong>{final_value.toFixed(2)}</strong></span>
//       </div>
//     </div>
//   );
// }

import React from "react";
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  Cell, ReferenceLine,
} from "recharts";

function shortenLabel(text, maxLen = 32) {
  const base = text.split(" (")[0].trim();
  const source = base.length >= 6 ? base : text;
  return source.length > maxLen ? source.slice(0, maxLen - 1) + "…" : source;
}

function CustomYAxisTick({ x, y, payload }) {
  const short = shortenLabel(payload.value);
  return (
    <g transform={`translate(${x},${y})`}>
      <text x={0} y={0} dy={4} textAnchor="end" fontSize={12} fill="#334155">
        {short}
        <title>{payload.value}</title>
      </text>
    </g>
  );
}

// Builds a plain-language takeaway from the real contributions, so it
// stays accurate for any prediction rather than being hardcoded text.
function buildPlainSummary(contributions, predictedClass) {
  const real = contributions.filter((c) => !c.feature.startsWith("other_"));
  if (real.length === 0) return null;

  const top = [...real].sort((a, b) => Math.abs(b.shap_value) - Math.abs(a.shap_value));
  const topPositive = top.find((c) => c.shap_value > 0);
  const secondPositive = top.find((c) => c.shap_value > 0 && c !== topPositive);
  const topNegative = top.find((c) => c.shap_value < 0);

  const label = (c) => (c.description || c.feature).split(" (")[0].trim();

  let sentence = `This water sample was mainly classified as "${predictedClass}" because of `;
  if (topPositive && secondPositive) {
    sentence += `${label(topPositive)} and ${label(secondPositive)}`;
  } else if (topPositive) {
    sentence += `${label(topPositive)}`;
  } else {
    sentence = `No single factor strongly stood out for this "${predictedClass}" prediction — it's based on a combination of smaller signals.`;
    return sentence;
  }

  if (topNegative) {
    sentence += `, despite ${label(topNegative)} pointing the other way`;
  }
  sentence += ".";
  return sentence;
}

export default function ShapWaterfall({ waterfall, narrative }) {
  if (!waterfall || !waterfall.contributions || waterfall.contributions.length === 0) {
    return <p className="empty-state">No explanation available yet.</p>;
  }

  const { base_value, final_value, predicted_class, contributions } = waterfall;

  let cumulative = base_value;
  const data = contributions.map((c) => {
    const start = cumulative;
    cumulative += c.shap_value;
    const end = cumulative;
    return {
      name: c.description || c.feature,
      spacer: Math.min(start, end),
      value: Math.abs(end - start),
      isPositive: c.shap_value >= 0,
      rawValue: c.shap_value,
    };
  });

  const rowHeight = 42;
  const chartHeight = Math.max(340, data.length * rowHeight + 60);
  const plainSummary = buildPlainSummary(contributions, predicted_class);

  return (
    <div className="shap-waterfall-card">
      <div className="shap-waterfall-header">
        <h3>Why "{predicted_class}"?</h3>
        {narrative && <p className="shap-narrative">{narrative}</p>}
      </div>

      <div className="shap-waterfall-legend">
        <span className="legend-item">
          <span className="legend-swatch increase" /> Pushes toward {predicted_class}
        </span>
        <span className="legend-item">
          <span className="legend-swatch decrease" /> Pushes away
        </span>
      </div>

      <ResponsiveContainer width="100%" height={chartHeight}>
        <BarChart
          data={data}
          layout="vertical"
          margin={{ top: 24, right: 60, left: 10, bottom: 10 }}
          barCategoryGap={14}
        >
          <CartesianGrid strokeDasharray="3 3" horizontal={false} />
          <XAxis type="number" tick={{ fontSize: 12 }} />
          <YAxis type="category" dataKey="name" width={210} tick={<CustomYAxisTick />} interval={0} />
          <Tooltip
            formatter={(_val, _name, props) => [
              `${props.payload.rawValue > 0 ? "+" : ""}${props.payload.rawValue.toFixed(3)}`,
              "Impact",
            ]}
            labelFormatter={(label) => label}
          />
          <ReferenceLine
            x={base_value}
            stroke="#94a3b8"
            strokeDasharray="4 4"
            label={{ value: "Base", position: "top", fontSize: 11, fill: "#64748b", offset: 8 }}
          />
          <ReferenceLine
            x={final_value}
            stroke="#1e293b"
            strokeWidth={1.5}
            label={{ value: "Prediction", position: "top", fontSize: 11, fill: "#1e293b", offset: 8 }}
          />
          <Bar dataKey="spacer" stackId="a" fill="transparent" isAnimationActive={false} />
          <Bar dataKey="value" stackId="a" radius={[3, 3, 3, 3]} barSize={18}>
            {data.map((entry, index) => (
              <Cell key={index} fill={entry.isPositive ? "#dc2626" : "#2563eb"} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>

      <div className="shap-waterfall-footer">
        <span>Base: <strong>{base_value.toFixed(2)}</strong></span>
        <span>→</span>
        <span>Final: <strong>{final_value.toFixed(2)}</strong></span>
      </div>

      {plainSummary && <p className="shap-plain-summary">{plainSummary}</p>}
    </div>
  );
}