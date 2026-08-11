import time, json, urllib.request, urllib.parse

USER_AGENT = "water-quality-fingerprinting-app/1.0 (student project)"

def geocode(query):
    url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode({
        "q": query, "format": "json", "limit": 1
    })
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=10) as resp:
        return json.loads(resp.read())

queries = [
    "Udhagamandalam Lake, Ooty, Tamil Nadu, India",
    "Ooty Lake, Tamil Nadu, India",
    "Udhagamandalam Lake, India",
    "Redhills Lake, Tiruvallur, Tamil Nadu, India",
    "Red Hills Lake, Chennai, India",
    "Redhills, Tamil Nadu, India",
]

for q in queries:
    print(f"\n{q!r}")
    try:
        data = geocode(q)
        if data:
            print(f"  FOUND: {data[0]['lat']}, {data[0]['lon']} -- {data[0]['display_name']}")
        else:
            print("  No results")
    except Exception as e:
        print(f"  EXCEPTION: {e}")
    time.sleep(1.2)