import urllib.request
import json
import ssl
import os

TARGET = "https://worldviewosint.com"
OUTDIR = r"C:\Users\mmrla\worldviewosnit\captures"
ctx = ssl.create_default_context()

endpoints = {
    "conflicts": "/api/osint/conflicts",
    "thermal": "/api/osint/thermal",
    "oryx": "/api/osint/oryx",
    "maritime": "/api/osint/maritime",
    "security": "/api/osint/security",
    "disasters": "/api/osint/disasters",
    "aviation": "/api/osint/aviation",
    "economic": "/api/osint/economic",
    "infra": "/api/osint/infra",
    "losses": "/api/osint/losses",
    "risk": "/api/risk-summary",
    "market": "/api/portfolio",
}

for name, path in endpoints.items():
    url = TARGET + path
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json"
        })
        resp = urllib.request.urlopen(req, timeout=30, context=ctx)
        body = resp.read().decode("utf-8", errors="replace")
        data = json.loads(body)
        fpath = os.path.join(OUTDIR, f"data_{name}.json")
        with open(fpath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        # Summary
        if isinstance(data, dict):
            for k, v in data.items():
                if isinstance(v, list):
                    print(f"  {name}/{k}: {len(v)} items")
                    if v:
                        print(f"    Sample keys: {list(v[0].keys()) if isinstance(v[0], dict) else type(v[0])}")
    except Exception as e:
        print(f"  ERROR {name}: {e}")

print("\nAll data saved to captures/data_*.json")
