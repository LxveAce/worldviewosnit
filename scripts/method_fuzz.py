import urllib.request
import urllib.error
import json
import time
import ssl

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
    "/api/ai/toggle",
    "/api/ai/force",
    "/api/telegram/report",
]

METHODS = ["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS", "HEAD"]

results = []

for ep in ENDPOINTS:
    url = TARGET + ep
    for method in METHODS:
        entry = {"endpoint": ep, "method": method, "status": None, "content_type": None, "body_preview": None, "interesting": False}
        try:
            if method in ("POST", "PUT", "PATCH"):
                data = json.dumps({"test": True}).encode("utf-8")
                req = urllib.request.Request(url, data=data, method=method, headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "application/json",
                    "Content-Type": "application/json",
                    "Origin": "https://worldviewosint.com",
                    "Referer": "https://worldviewosint.com/"
                })
            else:
                req = urllib.request.Request(url, method=method, headers={
                    "User-Agent": "Mozilla/5.0",
                    "Accept": "application/json"
                })
            resp = urllib.request.urlopen(req, timeout=10, context=ctx)
            entry["status"] = resp.status
            entry["content_type"] = resp.headers.get("Content-Type", "")
            if method == "OPTIONS":
                entry["allow"] = resp.headers.get("Allow", "")
                entry["access_control_allow_methods"] = resp.headers.get("Access-Control-Allow-Methods", "")
                entry["access_control_allow_origin"] = resp.headers.get("Access-Control-Allow-Origin", "")
                entry["access_control_allow_headers"] = resp.headers.get("Access-Control-Allow-Headers", "")
            if method != "HEAD":
                body = resp.read(1000).decode("utf-8", errors="replace")
                is_html = body.strip().startswith("<!DOCTYPE") or body.strip().startswith("<html")
                if not is_html:
                    entry["body_preview"] = body[:300]
                    entry["interesting"] = True
                else:
                    entry["body_preview"] = "[SPA HTML]"
            else:
                entry["content_length"] = resp.headers.get("Content-Length", "")
        except urllib.error.HTTPError as e:
            entry["status"] = e.code
            entry["content_type"] = e.headers.get("Content-Type", "") if e.headers else ""
            try:
                body = e.read(500).decode("utf-8", errors="replace")
                is_html = body.strip().startswith("<!DOCTYPE")
                if not is_html and body.strip():
                    entry["body_preview"] = body[:300]
                    entry["interesting"] = True
                else:
                    entry["body_preview"] = "[SPA HTML]" if is_html else "[empty]"
            except:
                pass
            if e.code not in (200, 404) and e.code != 405:
                entry["interesting"] = True
        except Exception as e:
            entry["status"] = "ERROR"
            entry["body_preview"] = str(e)[:200]

        flag = " ***" if entry["interesting"] else ""
        preview = (entry.get("body_preview") or "")[:80]
        print(f"  {method:7} {ep:35} => {str(entry['status']):>3} {preview}{flag}")
        results.append(entry)
        time.sleep(0.3)

with open(r"C:\Users\mmrla\worldviewosnit\logs\method_fuzz.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

interesting = [r for r in results if r.get("interesting")]
print(f"\n{'='*60}")
print(f"Total: {len(results)} | Interesting: {len(interesting)}")
print(f"{'='*60}")
if interesting:
    print("\nINTERESTING FINDINGS:")
    for r in interesting:
        print(f"  {r['method']:7} {r['endpoint']:35} => {r['status']} | {r.get('body_preview','')[:100]}")

print("\nSaved to logs/method_fuzz.json")
