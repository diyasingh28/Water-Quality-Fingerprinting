import React, { useState } from "react";

const PARAM_LABELS = {
  ph: "pH",
  dissolved_oxygen: "Dissolved Oxygen",
  bod: "BOD",
  conductivity: "Conductivity",
  nitrate: "Nitrate",
  fecal_coliform: "Fecal Coliform",
  total_coliform: "Total Coliform",
  temperature: "Temperature",
};

const PARAM_ORDER = Object.keys(PARAM_LABELS);

// category_ranges includes a "_rule_thresholds" key and possibly
// "unclassified" -- neither is useful to show as a comparison row.
const EXCLUDED_CATEGORIES = ["_rule_thresholds", "unclassified"];

function isWithinRange(value, range) {
  if (value == null || !range) return null;
  return value >= range.typical_low && value <= range.typical_high;
}

export default function CategoryRangeTable({ categoryRanges, sampleValues, predictedSource }) {
  const [open, setOpen] = useState(false);

  if (!categoryRanges || !sampleValues) return null;

  const categories = Object.keys(categoryRanges).filter(
    (c) => !EXCLUDED_CATEGORIES.includes(c)
  );

  return (
    <div className="range-table-card">
      <button
        className="range-table-toggle"
        onClick={() => setOpen((v) => !v)}
        aria-expanded={open}
      >
        <span>{open ? "▾" : "▸"} How does this compare to typical ranges?</span>
      </button>

      {open && (
        <div className="range-table-wrapper">
          <table className="range-table">
            <thead>
              <tr>
                <th>Parameter</th>
                <th className="your-value-col">Your Value</th>
                {categories.map((cat) => (
                  <th
                    key={cat}
                    className={cat === predictedSource ? "predicted-col" : ""}
                  >
                    {cat.replace(/_/g, " ")}
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {PARAM_ORDER.map((param) => (
                <tr key={param}>
                  <td className="param-name">{PARAM_LABELS[param]}</td>
                  <td className="your-value-col">
                    {sampleValues[param] != null ? sampleValues[param] : "—"}
                  </td>
                  {categories.map((cat) => {
                    const range = categoryRanges[cat]?.[param];
                    if (!range) return <td key={cat}>—</td>;
                    const within = isWithinRange(sampleValues[param], range);
                    return (
                      <td
                        key={cat}
                        className={[
                          cat === predictedSource ? "predicted-col" : "",
                          within ? "value-match" : "",
                        ].join(" ")}
                      >
                        {range.typical_low}–{range.typical_high}
                        {within && <span className="match-badge"> ✓</span>}
                      </td>
                    );
                  })}
                </tr>
              ))}
            </tbody>
          </table>
          {/* <p className="range-table-note">
            Ranges shown are the typical (25th–75th percentile) values observed
            for each category in the training data. A ✓ means your sample's
            value falls within that category's typical range.
          </p> */}
        </div>
      )}
    </div>
  );
}