"""Flags a reading as anomalous relative to the SAME station's own
history, computed directly from prior years' raw readings -- not from the
classifier's _rollmean/_rollstd features, which include the current row
in their window and would dilute the very spike we're trying to detect.
"""

import statistics

KEY_PARAMS = [
    "bod", "conductivity", "nitrate",
    "fecal_coliform", "total_coliform", "dissolved_oxygen",
]

Z_SCORE_THRESHOLD = 2.0
MIN_HISTORY_POINTS = 2  # need at least 2 prior years for a meaningful std


def _midpoint(d: dict, param: str):
    min_v = d.get(f"{param}_min")
    max_v = d.get(f"{param}_max")
    if min_v is None or max_v is None:
        return None
    return (min_v + max_v) / 2


def compute_anomaly(current_sample: dict, history_rows: list) -> dict:
    """current_sample and each item in history_rows share the same shape --
    a dict with {param}_min / {param}_max keys (the raw sample dict passed
    to inference.predict, and _reading_to_dict() output respectively)."""
    if len(history_rows) < MIN_HISTORY_POINTS:
        return {"is_anomaly": False, "anomalies": []}

    anomalies = []
    for param in KEY_PARAMS:
        hist_values = [v for h in history_rows if (v := _midpoint(h, param)) is not None]
        if len(hist_values) < MIN_HISTORY_POINTS:
            continue

        mean = statistics.mean(hist_values)
        std = statistics.stdev(hist_values)
        if std <= 0:
            continue

        current_value = _midpoint(current_sample, param)
        if current_value is None:
            continue

        z = (current_value - mean) / std
        if abs(z) >= Z_SCORE_THRESHOLD:
            anomalies.append({
                "parameter": param,
                "value": round(current_value, 2),
                "historical_mean": round(mean, 2),
                "historical_std": round(std, 2),
                "z_score": round(z, 2),
            })

    anomalies.sort(key=lambda a: abs(a["z_score"]), reverse=True)
    return {"is_anomaly": len(anomalies) > 0, "anomalies": anomalies}