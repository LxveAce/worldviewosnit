import urllib.request
import urllib.error
import json
import time
import ssl

TARGET = "https://worldviewosint.com"

# Now we know /api/health is real. Probe for more real API routes.
# The SPA returns HTML for fake routes, real APIs return JSON.
API_PATHS = [
    "/api/health",
    "/api/ais",
    "/api/ais/vessels",
    "/api/vessels",
    "/api/ships",
    "/api/maritime",
    "/api/conflicts",
    "/api/conflict",
    "/api/events",
    "/api/disasters",
    "/api/earthquakes",
    "/api/aviation",
    "/api/flights",
    "/api/aircraft",
    "/api/mil-aviation",
    "/api/civ-aviation",
    "/api/military",
    "/api/risk",
    "/api/riskdata",
    "/api/risk-data",
    "/api/threats",
    "/api/threat",
    "/api/news",
    "/api/feed",
    "/api/market",
    "/api/econ",
    "/api/economy",
    "/api/oryx",
    "/api/losses",
    "/api/thermal",
    "/api/infra",
    "/api/infrastructure",
    "/api/security",
    "/api/weather",
    "/api/map",
    "/api/globe",
    "/api/features",
    "/api/data",
    "/api/all",
    "/api/summary",
    "/api/dashboard",
    "/api/status",
    "/api/config",
    "/api/ai",
    "/api/ai/status",
    "/api/ai/analysis",
    "/api/analysis",
    "/api/analytics",
    "/api/telegram",
    "/api/notify",
    "/api/webhook",
    "/api/ws",
    "/api/socket",
    "/api/stream",
    "/api/live",
    "/api/realtime",
    "/api/geojson",
    "/api/markers",
    "/api/layers",
    "/api/alerts",
    "/api/v1/health",
    "/api/v1/data",
    "/api/v1/events",
    "/api/v2/health",
    "/api/v2/data",
    "/socket.io/?EIO=4&transport=polling",
]

ctx = ssl.create_default_context()
real_apis = []
spa_routes = []

for path in API_PATHS:
    url = TARGET + path
    entry = {
        "path": path,
        "status": None,
        "content_type": None,
        "is_real_api": False,
        "body": None
    }
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*"
        })
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        entry["status"] = resp.status
        entry["content_type"] = resp.headers.get("Content-Type", "")
        body = resp.read(5000).decode("utf-8", errors="replace")

        # Real API returns JSON, SPA catch-all returns HTML
        is_json = "application/json" in entry["content_type"]
        starts_html = body.strip().startswith("<!DOCTYPE") or body.strip().startswith("<html")

        if is_json or (not starts_html and body.strip().startswith("{")):
            entry["is_real_api"] = True
            entry["body"] = body[:2000]
            real_apis.append(entry)
            print(f"  [REAL API] {path} -> {entry['content_type']}")
            print(f"             {body[:200]}")
        else:
            entry["is_real_api"] = False
            spa_routes.append(path)
    except urllib.error.HTTPError as e:
        entry["status"] = e.code
        entry["content_type"] = e.headers.get("Content-Type", "")
        try:
            body = e.read(2000).decode("utf-8", errors="replace")
            if "application/json" in entry["content_type"] or body.strip().startswith("{"):
                entry["is_real_api"] = True
                entry["body"] = body[:2000]
                real_apis.append(entry)
                print(f"  [REAL API] [{e.code}] {path} -> {body[:200]}")
            else:
                spa_routes.append(path)
        except:
            spa_routes.append(path)
    except Exception as e:
        print(f"  [ERROR] {path} -> {e}")

    time.sleep(0.5)

print(f"\n{'='*60}")
print(f"REAL API ENDPOINTS: {len(real_apis)}")
print(f"SPA CATCH-ALL ROUTES: {len(spa_routes)}")
print(f"{'='*60}")

output = {
    "real_apis": real_apis,
    "spa_catch_all_count": len(spa_routes),
    "spa_catch_all_paths": spa_routes
}

with open(r"C:\Users\mmrla\worldviewosnit\logs\api_discovery.json", "w", encoding="utf-8") as f:
    json.dump(output, f, indent=2)

print("\nSaved to logs/api_discovery.json")
