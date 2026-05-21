import urllib.request
import ssl
import json
import time
import os
from datetime import datetime

TARGET = "https://worldviewosint.com"
ctx = ssl.create_default_context()

ENDPOINTS = {
    "health": "/api/health",
    "risk_summary": "/api/risk-summary",
    "conflicts": "/api/osint/conflicts",
    "thermal": "/api/osint/thermal",
    "oryx": "/api/osint/oryx",
    "maritime": "/api/osint/maritime",
    "security": "/api/osint/security",
    "disasters": "/api/osint/disasters",
    "aviation": "/api/osint/aviation",
    "portfolio": "/api/portfolio",
    "losses": "/api/osint/losses",
    "economic": "/api/osint/economic",
    "infra": "/api/osint/infra",
    "ai_status": "/api/ai/status",
}

timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
outdir = r"C:\Users\mmrla\worldviewosnit\captures\temporal"
os.makedirs(outdir, exist_ok=True)

capture = {"timestamp": timestamp, "iso": datetime.now().isoformat(), "endpoints": {}}

print(f"=== TEMPORAL DATA CAPTURE: {timestamp} ===\n")

for name, ep in ENDPOINTS.items():
    url = TARGET + ep
    try:
        start = time.time()
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        resp = urllib.request.urlopen(req, timeout=30, context=ctx)
        body = resp.read().decode("utf-8", errors="replace")
        elapsed_ms = round((time.time() - start) * 1000, 1)

        data = json.loads(body)

        # Extract key metrics
        summary = {}
        if name == "health":
            summary = {"version": data.get("v"), "uptime": data.get("up"), "mem": data.get("mem"), "ais_vessels": data.get("aisVessels")}
        elif name == "aviation":
            summary = {"milCount": data.get("milCount"), "civCount": data.get("civCount"), "vectors": len(data.get("vectors", []))}
        elif name == "maritime":
            ships = data.get("ships", [])
            summary = {"ship_count": len(ships), "first_mmsi": ships[0].get("mmsi") if ships else None}
        elif name == "conflicts":
            zones = data.get("zones", [])
            summary = {"zone_count": len(zones)}
        elif name == "disasters":
            events = data.get("events", [])
            summary = {"event_count": len(events), "first_event": events[0].get("name") if events else None}
        elif name == "thermal":
            hotspots = data.get("hotspots", [])
            summary = {"hotspot_count": len(hotspots)}
        elif name == "portfolio":
            market = data.get("market", {})
            summary = {"asset": market.get("asset"), "price": market.get("price")}
        elif name == "risk_summary":
            summary = {"riskScore": data.get("riskScore"), "alertLevel": data.get("alertLevel")}
        elif name == "ai_status":
            summary = {"enabled": data.get("enabled"), "callsToday": data.get("callsToday")}

        capture["endpoints"][name] = {
            "status": 200,
            "elapsed_ms": elapsed_ms,
            "summary": summary,
            "full_data": data,
        }
        print(f"  {name:15} {elapsed_ms:>7.1f}ms  {summary}")

    except Exception as e:
        print(f"  {name:15} ERROR: {e}")
        capture["endpoints"][name] = {"status": "error", "error": str(e)[:200]}
    time.sleep(0.3)

# Save capture
outfile = os.path.join(outdir, f"capture_{timestamp}.json")
with open(outfile, "w", encoding="utf-8") as f:
    json.dump(capture, f, indent=2)

# Also compare with previous captures if they exist
print(f"\n--- COMPARISON WITH PREVIOUS CAPTURES ---")
prev_dir = r"C:\Users\mmrla\worldviewosnit\captures"
prev_data = {}

# Load original data captures
for fname in os.listdir(prev_dir):
    if fname.startswith("data_") and fname.endswith(".json"):
        key = fname.replace("data_", "").replace(".json", "")
        try:
            with open(os.path.join(prev_dir, fname), "r") as f:
                prev_data[key] = json.load(f)
        except:
            pass

# Compare key metrics
changes = []
now = capture["endpoints"]

if "aviation" in now and "aviation" in prev_data:
    old_mil = prev_data["aviation"].get("milCount", "?")
    new_mil = now["aviation"]["summary"].get("milCount", "?")
    if old_mil != new_mil:
        changes.append(f"  Aviation: milCount {old_mil} -> {new_mil}")

if "portfolio" in now and "market" in prev_data:
    old_price = prev_data["market"].get("market", {}).get("price", "?")
    new_price = now["portfolio"]["summary"].get("price", "?")
    if old_price != new_price:
        changes.append(f"  BTC Price: {old_price} -> {new_price}")

if "disasters" in now and "disasters" in prev_data:
    old_count = len(prev_data["disasters"].get("events", []))
    new_count = now["disasters"]["summary"].get("event_count", "?")
    if old_count != new_count:
        changes.append(f"  Disasters: {old_count} -> {new_count} events")

if "maritime" in now and "maritime" in prev_data:
    old_count = len(prev_data["maritime"].get("ships", []))
    new_count = now["maritime"]["summary"].get("ship_count", "?")
    if old_count != new_count:
        changes.append(f"  Maritime: {old_count} -> {new_count} ships")

if "health" in now and "health" in prev_data:
    old_up = prev_data["health"].get("up", "?")
    new_up = now["health"]["summary"].get("uptime", "?")
    changes.append(f"  Uptime: {old_up} -> {new_up} seconds")

if changes:
    print("DATA CHANGES DETECTED:")
    for c in changes:
        print(c)
else:
    print("No changes detected (or no previous data to compare)")

print(f"\nSaved to {outfile}")
