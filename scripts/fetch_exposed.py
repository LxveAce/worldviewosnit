import urllib.request
import ssl
import json
import os

TARGET = "https://worldviewosint.com"
ctx = ssl.create_default_context()

EXPOSED_FILES = [
    "/docker-compose.yml",
    "/server.js",
    "/index.js",
    "/main.js",
    "/config.js",
    "/ecosystem.config.js",
    "/robots.txt",
    "/humans.txt",
    "/security.txt",
    "/.well-known/security.txt",
]

OUTDIR = r"C:\Users\mmrla\worldviewosnit\captures\exposed"
os.makedirs(OUTDIR, exist_ok=True)

results = {}

print("=== FETCHING EXPOSED FILES ===\n")

for path in EXPOSED_FILES:
    url = TARGET + path
    try:
        req = urllib.request.Request(url, headers={
            "User-Agent": "Mozilla/5.0",
            "Accept": "*/*"
        })
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        body = resp.read()
        content_type = resp.headers.get("Content-Type", "")
        size = len(body)

        text = body.decode("utf-8", errors="replace")
        is_html = text.strip().startswith("<!DOCTYPE") or text.strip().startswith("<html")

        filename = path.replace("/", "_").strip("_")
        if not filename:
            filename = "root"

        filepath = os.path.join(OUTDIR, filename)
        with open(filepath, "wb") as f:
            f.write(body)

        print(f"  {path}")
        print(f"    Size: {size} bytes | Content-Type: {content_type}")
        print(f"    HTML: {is_html} | Saved to: {filename}")
        if not is_html:
            print(f"    CONTENT: {text[:500]}")
            print()
        else:
            # Check if it's the SAME SPA or different
            if 20000 <= size <= 22000:
                print(f"    => Standard SPA catch-all ({size}B)")
            else:
                print(f"    => DIFFERENT SIZE from SPA ({size}B vs ~21130B)")
                # Show first non-HTML content or title differences
                import re
                title = re.search(r"<title>(.*?)</title>", text)
                if title:
                    print(f"    Title: {title.group(1)}")
        print()

        results[path] = {
            "size": size,
            "content_type": content_type,
            "is_html": is_html,
            "saved_as": filename,
            "preview": text[:1000] if not is_html else f"HTML ({size}B)"
        }

    except Exception as e:
        print(f"  {path} => ERROR: {e}")
        results[path] = {"error": str(e)}

# Also try to fetch the AI analyze endpoint with different methods
print("\n=== NEW ENDPOINT: /api/ai/analyze ===")
for method in ["GET", "POST", "OPTIONS"]:
    try:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        }
        if method == "POST":
            data = json.dumps({"query": "test"}).encode("utf-8")
            headers["Content-Type"] = "application/json"
            req = urllib.request.Request(TARGET + "/api/ai/analyze", data=data, method=method, headers=headers)
        elif method == "OPTIONS":
            headers["Origin"] = "https://worldviewosint.com"
            headers["Access-Control-Request-Method"] = "POST"
            req = urllib.request.Request(TARGET + "/api/ai/analyze", method=method, headers=headers)
        else:
            req = urllib.request.Request(TARGET + "/api/ai/analyze", method=method, headers=headers)

        resp = urllib.request.urlopen(req, timeout=10, context=ctx)
        body = resp.read(2000).decode("utf-8", errors="replace")
        print(f"  {method} => {resp.status} | {body[:200]}")
        acao = resp.headers.get("Access-Control-Allow-Origin", "")
        if acao:
            print(f"    ACAO: {acao}")
        results[f"ai_analyze_{method}"] = {"status": resp.status, "body": body[:500]}
    except Exception as e:
        error_str = str(e)
        print(f"  {method} => {error_str[:100]}")
        # Try to read error body
        if hasattr(e, 'read'):
            try:
                err_body = e.read(500).decode("utf-8", errors="replace")
                print(f"    Body: {err_body[:200]}")
                results[f"ai_analyze_{method}"] = {"error": error_str[:200], "body": err_body[:500]}
            except:
                pass

with open(r"C:\Users\mmrla\worldviewosnit\logs\exposed_files.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print("\nSaved to logs/exposed_files.json")
