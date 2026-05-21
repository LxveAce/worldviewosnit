import urllib.request
import urllib.error
import json
import time
import ssl
import base64

# Decode Mapbox token to extract username
print("=== MAPBOX TOKEN DECODE ===")
token = "pk.eyJ1IjoianVhbmVzMjc5NCIsImEiOiJjbW45a2lqa2swYTN5Mm9vNGgzY3pqcmRyIn0.[REDACTED]"
parts = token.split(".")
try:
    payload = parts[1]
    payload += "=" * (4 - len(payload) % 4)
    decoded = base64.b64decode(payload).decode("utf-8")
    print(f"Token payload: {decoded}")
except Exception as e:
    print(f"Decode error: {e}")
print()

# Now probe all REAL API endpoints found in app.js
TARGET = "https://worldviewosint.com"
REAL_APIS = [
    "/api/health",
    "/api/risk-summary",
    "/api/osint/conflicts",
    "/api/osint/thermal",
    "/api/osint/oryx",
    "/api/osint/maritime",
    "/api/osint/security",
    "/api/osint/disasters",
    "/api/osint/aviation",
    "/api/portfolio",
    "/api/osint/losses",
    "/api/osint/economic",
    "/api/osint/infra",
    "/api/ai/status",
    "/api/telegram/report",
]

ctx = ssl.create_default_context()
results = {}

for path in REAL_APIS:
    url = TARGET + path
    print(f"Probing {path}...")
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Accept": "application/json, text/plain, */*",
        })
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        content_type = resp.headers.get("Content-Type", "")
        body = resp.read(10000).decode("utf-8", errors="replace")

        is_json = "application/json" in content_type
        is_html = body.strip().startswith("<!DOCTYPE") or body.strip().startswith("<html")

        if is_html:
            results[path] = {"status": resp.status, "type": "SPA_CATCH_ALL", "data": None}
            print(f"  -> SPA catch-all (HTML)")
        elif is_json or body.strip().startswith("{") or body.strip().startswith("["):
            try:
                data = json.loads(body)
                results[path] = {"status": resp.status, "type": "REAL_API", "data": data}
                # Print summary
                if isinstance(data, dict):
                    keys = list(data.keys())
                    print(f"  -> JSON ({resp.status}) keys: {keys}")
                    # Count arrays
                    for k, v in data.items():
                        if isinstance(v, list):
                            print(f"     {k}: {len(v)} items")
                        elif isinstance(v, dict):
                            print(f"     {k}: {json.dumps(v)[:100]}")
                        else:
                            print(f"     {k}: {str(v)[:100]}")
                elif isinstance(data, list):
                    print(f"  -> JSON array ({resp.status}) {len(data)} items")
            except json.JSONDecodeError:
                results[path] = {"status": resp.status, "type": "TEXT", "data": body[:500]}
                print(f"  -> Non-JSON text: {body[:200]}")
        else:
            results[path] = {"status": resp.status, "type": "OTHER", "data": body[:500]}
            print(f"  -> Other: {body[:200]}")
    except urllib.error.HTTPError as e:
        body = ""
        try:
            body = e.read(5000).decode("utf-8", errors="replace")
        except:
            pass
        results[path] = {"status": e.code, "type": "ERROR", "data": body[:500]}
        print(f"  -> HTTP {e.code}: {body[:200]}")
    except Exception as e:
        results[path] = {"status": "ERROR", "type": "EXCEPTION", "data": str(e)}
        print(f"  -> Exception: {e}")

    time.sleep(0.5)

# Save full results
with open(r"C:\Users\mmrla\worldviewosnit\logs\api_responses.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)

print(f"\nSaved {len(results)} API responses to logs/api_responses.json")

# Summary
real = [p for p, r in results.items() if r["type"] == "REAL_API"]
spa = [p for p, r in results.items() if r["type"] == "SPA_CATCH_ALL"]
errors = [p for p, r in results.items() if r["type"] == "ERROR"]
print(f"\nREAL APIs: {len(real)} | SPA fallback: {len(spa)} | Errors: {len(errors)}")
