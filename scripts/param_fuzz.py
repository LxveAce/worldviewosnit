import urllib.request
import urllib.error
import json
import ssl
import time

TARGET = "https://worldviewosint.com"
ctx = ssl.create_default_context()

SPA_SIZE_MIN = 20000
SPA_SIZE_MAX = 22000

def fetch(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        body = resp.read(10000).decode("utf-8", errors="replace")
        return resp.status, body
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read(5000).decode("utf-8", errors="replace")
        except:
            pass
        return e.code, body
    except Exception as e:
        return "ERR", str(e)

results = {}

# Test maritime with limit/all params (server has 269, client gets 50)
print("=== MARITIME PARAMETER FUZZING ===")
maritime_params = [
    "",
    "?limit=1",
    "?limit=5",
    "?limit=100",
    "?limit=300",
    "?limit=1000",
    "?all=true",
    "?full=true",
    "?raw=true",
    "?format=geojson",
    "?format=csv",
    "?mmsi=477995030",
    "?id=477995030",
    "?history=true",
    "?verbose=true",
    "?debug=true",
]
for param in maritime_params:
    url = TARGET + "/api/osint/maritime" + param
    status, body = fetch(url)
    is_html = body.strip().startswith("<!DOCTYPE")
    if not is_html and status == 200:
        try:
            data = json.loads(body)
            ships = data.get("ships", [])
            print(f"  {param or '(none)':30} => {status} | {len(ships)} ships")
            results[f"maritime{param}"] = {"status": status, "ships": len(ships)}
        except:
            print(f"  {param or '(none)':30} => {status} | non-JSON: {body[:80]}")
            results[f"maritime{param}"] = {"status": status, "body": body[:200]}
    else:
        print(f"  {param or '(none)':30} => {status} | {'HTML' if is_html else body[:80]}")
    time.sleep(0.4)

# Test aviation params
print("\n=== AVIATION PARAMETER FUZZING ===")
aviation_params = [
    "",
    "?military=true",
    "?military=false",
    "?civilian=true",
    "?limit=1000",
    "?source=opensky",
    "?source=adsb.lol",
    "?country=US",
    "?callsign=JANET",
    "?all=true",
    "?debug=true",
    "?verbose=true",
]
for param in aviation_params:
    url = TARGET + "/api/osint/aviation" + param
    status, body = fetch(url)
    is_html = body.strip().startswith("<!DOCTYPE")
    if not is_html and status == 200:
        try:
            data = json.loads(body)
            mil = data.get("milCount", "?")
            civ = data.get("civCount", "?")
            vectors = len(data.get("vectors", []))
            print(f"  {param or '(none)':30} => {status} | mil={mil} civ={civ} vectors={vectors}")
            results[f"aviation{param}"] = {"status": status, "mil": mil, "civ": civ, "vectors": vectors}
        except:
            print(f"  {param or '(none)':30} => {status} | non-JSON: {body[:80]}")
    else:
        print(f"  {param or '(none)':30} => {status} | {'HTML' if is_html else body[:80]}")
    time.sleep(0.4)

# Test conflicts with filtering params
print("\n=== CONFLICTS PARAMETER FUZZING ===")
conflict_params = [
    "",
    "?region=Ukraine",
    "?region=Donetsk",
    "?intensity=CRITICAL",
    "?type=ACTIVE_COMBAT",
    "?limit=5",
    "?limit=100",
    "?all=true",
    "?format=geojson",
    "?debug=true",
]
for param in conflict_params:
    url = TARGET + "/api/osint/conflicts" + param
    status, body = fetch(url)
    is_html = body.strip().startswith("<!DOCTYPE")
    if not is_html and status == 200:
        try:
            data = json.loads(body)
            zones = len(data.get("zones", []))
            print(f"  {param or '(none)':30} => {status} | {zones} zones")
            results[f"conflicts{param}"] = {"status": status, "zones": zones}
        except:
            print(f"  {param or '(none)':30} => {status} | {body[:80]}")
    else:
        print(f"  {param or '(none)':30} => {status} | {'HTML' if is_html else body[:80]}")
    time.sleep(0.4)

# Test health/risk with debug params
print("\n=== HEALTH / DEBUG PARAMETER FUZZING ===")
debug_params = [
    ("/api/health", "?verbose=true"),
    ("/api/health", "?debug=true"),
    ("/api/health", "?format=detailed"),
    ("/api/health", "?full=true"),
    ("/api/risk-summary", "?verbose=true"),
    ("/api/risk-summary", "?debug=true"),
    ("/api/risk-summary", "?detailed=true"),
    ("/api/ai/status", "?verbose=true"),
    ("/api/ai/status", "?debug=true"),
    ("/api/ai/status", "?history=true"),
]
for ep, param in debug_params:
    url = TARGET + ep + param
    status, body = fetch(url)
    is_html = body.strip().startswith("<!DOCTYPE")
    if not is_html and status == 200:
        print(f"  {ep+param:45} => {status} | {body[:120]}")
    else:
        print(f"  {ep+param:45} => {status} | HTML")
    time.sleep(0.4)

# NoSQL injection tests
print("\n=== NoSQL INJECTION TESTS ===")
nosql_params = [
    ("/api/osint/conflicts", "?intensity[$ne]=null"),
    ("/api/osint/conflicts", "?intensity[$gt]="),
    ("/api/osint/maritime", "?mmsi[$gt]=0"),
    ("/api/osint/maritime", "?mmsi[$regex]=.*"),
    ("/api/osint/conflicts", "?$where=1"),
    ("/api/osint/aviation", "?military[$ne]=false"),
    ("/api/health", "?status[$ne]=null"),
]
for ep, param in nosql_params:
    url = TARGET + ep + param
    status, body = fetch(url)
    is_html = body.strip().startswith("<!DOCTYPE")
    if not is_html and status == 200:
        try:
            data = json.loads(body)
            key = list(data.keys())
            print(f"  {ep+param:50} => {status} | keys={key[:5]}")
        except:
            print(f"  {ep+param:50} => {status} | {body[:80]}")
    elif status == 500:
        print(f"  [!!!] {ep+param:47} => {status} | SERVER ERROR: {body[:100]}")
    else:
        print(f"  {ep+param:50} => {status} | {'HTML' if is_html else body[:60]}")
    time.sleep(0.4)

with open(r"C:\Users\mmrla\worldviewosnit\logs\param_fuzz.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print("\nSaved to logs/param_fuzz.json")
