import urllib.request
import ssl
import time
import json

TARGET = "https://worldviewosint.com"
ctx = ssl.create_default_context()

ENDPOINTS = [
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
]

RUNS = 3
results = {}

print(f"Running {RUNS} timing samples per endpoint...\n")
print(f"{'Endpoint':<35} {'Run 1':>8} {'Run 2':>8} {'Run 3':>8} {'Avg':>8}  Classification")
print("-" * 100)

for ep in ENDPOINTS:
    url = TARGET + ep
    times = []
    for i in range(RUNS):
        start = time.time()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
            resp = urllib.request.urlopen(req, timeout=30, context=ctx)
            body = resp.read()
            elapsed = (time.time() - start) * 1000
            times.append(round(elapsed, 1))
        except Exception as e:
            times.append(-1)
        time.sleep(0.5)

    avg = round(sum(t for t in times if t > 0) / max(len([t for t in times if t > 0]), 1), 1)

    if avg < 150:
        classification = "CACHED/IN-MEMORY"
    elif avg < 500:
        classification = "SERVER COMPUTATION"
    else:
        classification = "EXTERNAL API CALL"

    results[ep] = {"times_ms": times, "avg_ms": avg, "classification": classification}
    t_str = "  ".join(f"{t:>6.1f}" for t in times)
    print(f"  {ep:<33} {t_str}  {avg:>6.1f}  {classification}")

with open(r"C:\Users\mmrla\worldviewosnit\logs\timing_analysis.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

print(f"\nSaved to logs/timing_analysis.json")
