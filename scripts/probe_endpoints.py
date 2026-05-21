import urllib.request
import urllib.error
import json
import time
import ssl

TARGET = "https://worldviewosint.com"
PATHS = [
    "/robots.txt",
    "/sitemap.xml",
    "/.well-known/security.txt",
    "/.well-known/openapi.json",
    "/api",
    "/api/v1",
    "/api/v2",
    "/api/health",
    "/api/hello",
    "/api/data",
    "/api/events",
    "/api/threats",
    "/api/status",
    "/health",
    "/healthcheck",
    "/status",
    "/metrics",
    "/graphql",
    "/.env",
    "/config.json",
    "/docs",
    "/redoc",
    "/openapi.json",
    "/admin",
    "/debug",
    "/internal",
    "/manifest.json",
    "/favicon.ico",
    "/sw.js",
    "/service-worker.js",
    "/.vercel/",
    "/_vercel/insights/script.js",
    "/feed",
    "/rss",
    "/feed.xml",
    "/_next/data/",
    "/assets/",
    "/js/",
    "/css/",
    "/static/",
    "/dist/",
    "/public/",
    "/login",
    "/dashboard",
    "/map",
    "/globe",
    "/socket.io/",
    "/ws",
    "/websocket",
]

results = []
ctx = ssl.create_default_context()

for path in PATHS:
    url = TARGET + path
    entry = {
        "path": path,
        "url": url,
        "status": None,
        "content_type": None,
        "content_length": None,
        "server": None,
        "classification": None,
        "redirect": None,
        "notes": ""
    }
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        })
        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        entry["status"] = resp.status
        entry["content_type"] = resp.headers.get("Content-Type", "")
        entry["content_length"] = resp.headers.get("Content-Length", "")
        entry["server"] = resp.headers.get("Server", "")
        body = resp.read(2000).decode("utf-8", errors="replace")
        if not entry["content_length"]:
            entry["content_length"] = str(len(body))
        entry["body_preview"] = body[:500]
        if resp.url != url:
            entry["redirect"] = resp.url
        entry["classification"] = "valid"
    except urllib.error.HTTPError as e:
        entry["status"] = e.code
        entry["content_type"] = e.headers.get("Content-Type", "")
        entry["server"] = e.headers.get("Server", "")
        try:
            body = e.read(1000).decode("utf-8", errors="replace")
            entry["body_preview"] = body[:500]
        except:
            entry["body_preview"] = ""
        if e.code == 404:
            entry["classification"] = "dead"
        elif e.code == 403:
            entry["classification"] = "forbidden"
        elif e.code == 301 or e.code == 302:
            entry["classification"] = "redirect"
            entry["redirect"] = e.headers.get("Location", "")
        else:
            entry["classification"] = "error"
    except Exception as e:
        entry["status"] = "TIMEOUT/ERROR"
        entry["classification"] = "error"
        entry["notes"] = str(e)

    status_str = str(entry["status"])
    cls = entry["classification"] or "unknown"
    print(f"  [{status_str:>3}] {cls:<10} {path}")
    results.append(entry)
    time.sleep(0.5)

with open(r"C:\Users\mmrla\worldviewosnit\logs\endpoints.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)

valid = [r for r in results if r["classification"] == "valid"]
dead = [r for r in results if r["classification"] == "dead"]
forbidden = [r for r in results if r["classification"] == "forbidden"]
errors = [r for r in results if r["classification"] == "error"]
print(f"\nSummary: {len(valid)} valid, {len(dead)} dead, {len(forbidden)} forbidden, {len(errors)} errors out of {len(results)} probed")
print("Results saved to logs/endpoints.json")
