
import time
import json
import logging
import urllib.request
import urllib.parse

logger = logging.getLogger("uvicorn.error")

USER_AGENT = "water-quality-fingerprinting-app/1.0 (student project)"
_last_request_time = 0.0
MIN_INTERVAL_SECONDS = 1.1  # stay under Nominatim's 1 req/sec limit

# Common run-together state/UT names seen in CPCB data -> correctly spaced
_STATE_FIXUPS = {
    "TAMILNADU": "TAMIL NADU",
    "ANDHRAPRADESH": "ANDHRA PRADESH",
    "MADHYAPRADESH": "MADHYA PRADESH",
    "UTTARPRADESH": "UTTAR PRADESH",
    "HIMACHALPRADESH": "HIMACHAL PRADESH",
    "WESTBENGAL": "WEST BENGAL",
}
 
# Connector/noise words that hurt Nominatim matching when left in
_DROP_WORDS = {"AT", "NEAR", "DIST", "DIST.", "DISTRICT", "TALUK", "TALUKA", "VILLAGE", "PANCHAYAT"}
 
 
# Manual overrides for stations whose CPCB name doesn't match how the
# place is actually indexed on OpenStreetMap (misspellings, alternate
# names, or names too generic/non-existent to geocode automatically).
# Keyed by a distinctive substring of the raw station name (checked
# case-insensitively), value is the query to send instead.
_MANUAL_OVERRIDES = {
    "KODAI KANAL": "Kodaikanal Lake, Tamil Nadu",
    "UDHAGAMADALEM": "Ooty Lake, Tamil Nadu",
    "REDD HILLS": "Redhills, Tamil Nadu",
    "PULICATE LAKE": "Pulicat Lake, Tamil Nadu",
}
 
 
def _clean_query(raw_name: str) -> str:
    """Turn a verbose CPCB station name into a search-friendly place query."""
    name = raw_name.upper()
 
    for wrong, right in _STATE_FIXUPS.items():
        name = name.replace(wrong, right)
 
    parts = [p.strip() for p in name.split(",")]
    parts = [p for p in parts if p]
 
    cleaned_parts = []
    for part in parts:
        words = [w for w in part.split() if w not in _DROP_WORDS]
        if words:
            cleaned_parts.append(" ".join(words))
 
    # Keep it short -- first 2-3 meaningful parts are usually enough
    # (lake name + district/state); extra boilerplate parts hurt matching
    query = ", ".join(cleaned_parts[:3])
 
    return query.title()
 
 
def geocode(query: str):
    """
    Look up a place name via Nominatim. Returns (lat, lon) or (None, None)
    if not found or on error. Self-rate-limits across calls in this process.
    """
    global _last_request_time
 
    elapsed = time.time() - _last_request_time
    if elapsed < MIN_INTERVAL_SECONDS:
        time.sleep(MIN_INTERVAL_SECONDS - elapsed)
 
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
        "q": query,
        "format": "json",
        "limit": 1,
    })
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
 
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            data = json.loads(resp.read())
        _last_request_time = time.time()
        if data:
            return float(data[0]["lat"]), float(data[0]["lon"])
    except Exception as e:
        logger.warning(f"Geocoding failed for '{query}': {e}")
        _last_request_time = time.time()
 
    return None, None
 
 
def geocode_station(raw_name: str, fallback: str = "India"):
    """
    Geocode a raw CPCB station name, cleaning it up first for better
    match rates. Falls back to just the first segment if the fuller
    cleaned query doesn't resolve.
    """
    if not raw_name:
        return geocode(fallback)
 
    raw_upper = raw_name.upper()
    for key, override_query in _MANUAL_OVERRIDES.items():
        if key in raw_upper:
            lat, lon = geocode(f"{override_query}, India")
            if lat is not None:
                return lat, lon
            break  # fall through to generic cleanup if override also fails
 
    cleaned = _clean_query(raw_name)
    lat, lon = geocode(f"{cleaned}, India")
    if lat is not None:
        return lat, lon
 
    # Second attempt: just the first comma-separated segment (usually
    # the lake name itself) plus India, in case the fuller query was
    # still too noisy for Nominatim's matcher.
    first_segment = raw_name.split(",")[0].strip().title()
    return geocode(f"{first_segment}, India")