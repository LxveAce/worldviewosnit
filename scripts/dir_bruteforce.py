import urllib.request
import urllib.error
import ssl
import time
import json

TARGET = "https://worldviewosint.com"
ctx = ssl.create_default_context()

SPA_SIZE_MIN = 20000
SPA_SIZE_MAX = 22000

WORDLIST = [
    # Node.js specific
    "/package.json", "/package-lock.json", "/yarn.lock", "/pnpm-lock.yaml",
    "/server.js", "/index.js", "/app.js", "/main.js",
    "/.npmrc", "/.node-version", "/.nvmrc",
    "/node_modules/.package-lock.json",
    # Config / DevOps
    "/.gitignore", "/.git/HEAD", "/.git/config", "/.git/refs/heads/main",
    "/docker-compose.yml", "/docker-compose.yaml", "/Dockerfile", "/.dockerignore",
    "/ecosystem.config.js", "/ecosystem.config.cjs",
    "/Procfile", "/Caddyfile", "/nginx.conf",
    "/.env", "/.env.local", "/.env.production", "/.env.development", "/.env.example",
    "/config.json", "/config.js", "/settings.json",
    "/tsconfig.json", "/jsconfig.json",
    # Hidden API routes
    "/api/v1", "/api/v2", "/api/v3",
    "/api/internal", "/api/admin", "/api/debug", "/api/test",
    "/api/osint/all", "/api/export", "/api/dump", "/api/backup",
    "/api/users", "/api/auth", "/api/login", "/api/register",
    "/api/sessions", "/api/logs", "/api/webhook", "/api/webhooks",
    "/api/cron", "/api/config", "/api/env",
    "/api/metrics", "/api/prometheus", "/api/grafana",
    "/api/swagger", "/api/docs", "/api/openapi",
    "/api/graphql", "/graphql",
    "/api/socket", "/api/socket.io",
    "/api/status", "/api/info", "/api/version",
    "/api/data", "/api/raw",
    "/api/osint/weather", "/api/osint/cyber", "/api/osint/sanctions",
    "/api/osint/nuclear", "/api/osint/space", "/api/osint/news",
    "/api/osint/social", "/api/osint/darkweb",
    "/api/telegram/status", "/api/telegram/send", "/api/telegram/webhook",
    "/api/ai/analyze", "/api/ai/prompt", "/api/ai/history", "/api/ai/config",
    # Admin / debug panels
    "/admin", "/admin/", "/admin/login", "/dashboard",
    "/_debug", "/__debug__", "/debug",
    "/console", "/shell", "/terminal",
    "/phpmyadmin", "/adminer",
    "/wp-admin", "/wp-login.php",
    # Common exposed files
    "/robots.txt", "/sitemap.xml", "/humans.txt", "/security.txt",
    "/.well-known/security.txt",
    "/crossdomain.xml", "/clientaccesspolicy.xml",
    "/swagger.json", "/openapi.json", "/api-docs",
    "/health", "/healthz", "/ready", "/readiness", "/liveness",
    "/info", "/actuator", "/actuator/health",
    # Source maps
    "/app.js.map", "/main.js.map", "/bundle.js.map",
    "/static/js/main.js.map",
    # Backup files
    "/backup.sql", "/dump.sql", "/db.sql",
    "/backup.tar.gz", "/backup.zip",
    "/server.js.bak", "/app.js.bak",
    # PM2 / process manager
    "/pm2.json", "/process.json",
    # SSL / certs
    "/.well-known/acme-challenge/test",
]

results = {"spa_catchall": [], "distinct": [], "errors": []}

print(f"=== Directory Brute-Force ({len(WORDLIST)} paths) ===\n")
print(f"SPA catch-all filter: {SPA_SIZE_MIN}-{SPA_SIZE_MAX} bytes\n")
print(f"{'Path':<55} {'Status':>6} {'Size':>7}  Classification")
print("-" * 100)

for path in WORDLIST:
    url = TARGET + path
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*"
        })
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        body = resp.read(25000)
        status = resp.status
        size = len(body)
        content_type = resp.headers.get("Content-Type", "")

        is_spa = SPA_SIZE_MIN <= size <= SPA_SIZE_MAX and (b"<!DOCTYPE" in body[:100] or b"<html" in body[:100])

        if is_spa:
            print(f"  {path:<53} {status:>6} {size:>6}B  SPA catch-all")
            results["spa_catchall"].append(path)
        else:
            preview = body[:120].decode("utf-8", errors="replace").replace("\n", " ")
            print(f"  [!!!] {path:<50} {status:>6} {size:>6}B  DISTINCT: {preview[:60]}")
            results["distinct"].append({
                "path": path,
                "status": status,
                "size": size,
                "content_type": content_type,
                "preview": body[:500].decode("utf-8", errors="replace")
            })
    except urllib.error.HTTPError as e:
        if e.code in (403, 401):
            print(f"  [***] {path:<50} {e.code:>6}         AUTH REQUIRED")
            results["distinct"].append({"path": path, "status": e.code, "note": "auth required"})
        elif e.code == 404:
            print(f"  {path:<53} {e.code:>6}         Not Found")
        elif e.code == 405:
            print(f"  [**]  {path:<50} {e.code:>6}         Method Not Allowed")
            results["distinct"].append({"path": path, "status": e.code, "note": "method not allowed"})
        else:
            print(f"  {path:<53} {e.code:>6}")
    except Exception as e:
        err = str(e)[:60]
        print(f"  {path:<53}    ERR  {err}")
        results["errors"].append({"path": path, "error": str(e)[:200]})
    time.sleep(0.3)

print(f"\n{'='*60}")
print(f"Total paths tested: {len(WORDLIST)}")
print(f"SPA catch-all: {len(results['spa_catchall'])}")
print(f"Distinct responses: {len(results['distinct'])}")
print(f"Errors: {len(results['errors'])}")
print(f"{'='*60}")

if results["distinct"]:
    print("\n[!!!] DISTINCT (NON-SPA) RESPONSES:")
    for r in results["distinct"]:
        print(f"  {r['path']} => {r.get('status','')} {r.get('note','')}")

with open(r"C:\Users\mmrla\worldviewosnit\logs\dir_bruteforce.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print("\nSaved to logs/dir_bruteforce.json")
