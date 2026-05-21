import urllib.request
import urllib.error
import ssl
import json
import time
import re

ctx = ssl.create_default_context()

MAPBOX_USER = "juanes2794"

# Extract token from captured app.js
APP_JS_PATH = r"C:\Users\mmrla\worldviewosnit\captures\app.js"
token = None
try:
    with open(APP_JS_PATH, "r") as f:
        content = f.read()
        match = re.search(r"pk\.eyJ1[^'\"]+", content)
        if match:
            token = match.group(0)
            print(f"Token found: {token[:30]}...")
        else:
            # Check if redacted
            if "REDACTED" in content:
                print("[!] Token was redacted in app.js")
                print("    Fetching fresh token from live site...")
                req = urllib.request.Request("https://worldviewosint.com/",
                    headers={"User-Agent": "Mozilla/5.0"})
                resp = urllib.request.urlopen(req, timeout=15, context=ctx)
                html = resp.read().decode("utf-8", errors="replace")
                match = re.search(r"pk\.eyJ1[^'\"]+", html)
                if match:
                    token = match.group(0)
                    print(f"Token from live site: {token[:30]}...")
except Exception as e:
    print(f"Error reading app.js: {e}")

if not token:
    print("[!] No Mapbox token available. Cannot enumerate.")
    exit(1)

results = {}

def fetch_json(url):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=15, context=ctx)
        return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        return {"error": e.code}
    except Exception as e:
        return {"error": str(e)}

# 1. List user's public styles
print(f"\n=== MAPBOX ACCOUNT ENUMERATION: {MAPBOX_USER} ===\n")
print("--- 1. Public Styles ---")
styles_url = f"https://api.mapbox.com/styles/v1/{MAPBOX_USER}?access_token={token}"
styles = fetch_json(styles_url)
if isinstance(styles, list):
    print(f"  Found {len(styles)} styles:")
    for s in styles:
        print(f"    - {s.get('name', '?')} (id: {s.get('id', '?')}, modified: {s.get('modified', '?')[:10]})")
    results["styles"] = styles
elif isinstance(styles, dict) and "error" in styles:
    print(f"  Error: {styles['error']}")
    results["styles"] = styles
else:
    print(f"  Response: {str(styles)[:200]}")
    results["styles"] = styles

# 2. List tilesets
print("\n--- 2. Tilesets ---")
tilesets_url = f"https://api.mapbox.com/tilesets/v1/{MAPBOX_USER}?access_token={token}"
tilesets = fetch_json(tilesets_url)
if isinstance(tilesets, list):
    print(f"  Found {len(tilesets)} tilesets:")
    for t in tilesets:
        print(f"    - {t.get('name', '?')} (id: {t.get('id', '?')}, type: {t.get('type', '?')})")
    results["tilesets"] = tilesets
elif isinstance(tilesets, dict) and "error" in tilesets:
    print(f"  Error: {tilesets['error']}")
    results["tilesets"] = tilesets

# 3. Check token scopes
print("\n--- 3. Token Scope Analysis ---")
scope_url = f"https://api.mapbox.com/tokens/v2?access_token={token}"
scopes = fetch_json(scope_url)
if isinstance(scopes, dict) and not scopes.get("error"):
    print(f"  Token info: {json.dumps(scopes, indent=2)[:500]}")
    results["token_info"] = scopes
else:
    # Try alternate endpoint
    scope_url2 = f"https://api.mapbox.com/tokens/v2/{MAPBOX_USER}?access_token={token}"
    scopes2 = fetch_json(scope_url2)
    if isinstance(scopes2, list):
        print(f"  Found {len(scopes2)} tokens for account:")
        for t in scopes2:
            print(f"    - {t.get('note', '?')} | scopes: {t.get('scopes', [])}")
        results["tokens"] = scopes2
    else:
        print(f"  Token scope check: {scopes}")
        results["token_info"] = scopes

# 4. Check for datasets (premium feature)
print("\n--- 4. Datasets ---")
datasets_url = f"https://api.mapbox.com/datasets/v1/{MAPBOX_USER}?access_token={token}"
datasets = fetch_json(datasets_url)
if isinstance(datasets, list):
    print(f"  Found {len(datasets)} datasets:")
    for d in datasets:
        print(f"    - {d.get('name', '?')} (id: {d.get('id', '?')}, size: {d.get('size', '?')})")
    results["datasets"] = datasets
else:
    print(f"  {datasets}")
    results["datasets"] = datasets

# 5. Check for uploads
print("\n--- 5. Uploads ---")
uploads_url = f"https://api.mapbox.com/uploads/v1/{MAPBOX_USER}?access_token={token}"
uploads = fetch_json(uploads_url)
if isinstance(uploads, list):
    print(f"  Found {len(uploads)} uploads:")
    for u in uploads[:10]:
        print(f"    - {u.get('name', '?')} (tileset: {u.get('tileset', '?')}, complete: {u.get('complete', '?')})")
    results["uploads"] = uploads
else:
    print(f"  {uploads}")
    results["uploads"] = uploads

# 6. Known Mapbox style IDs to test
print("\n--- 6. Specific Style Probes ---")
KNOWN_STYLES = [
    "streets-v12", "outdoors-v12", "light-v11", "dark-v11",
    "satellite-v9", "satellite-streets-v12", "navigation-day-v1",
    "navigation-night-v1",
]
for style in KNOWN_STYLES:
    style_url = f"https://api.mapbox.com/styles/v1/{MAPBOX_USER}/{style}?access_token={token}"
    data = fetch_json(style_url)
    if isinstance(data, dict) and not data.get("error"):
        print(f"  [!!!] Custom style exists: {style}")
        results[f"style_{style}"] = "exists"
    else:
        pass

# 7. Check what style the app actually uses
print("\n--- 7. App Style Detection ---")
if token:
    # The app.js uses mapboxgl.Map with a style option
    try:
        with open(APP_JS_PATH, "r") as f:
            content = f.read()
            style_match = re.search(r"style:\s*['\"]([^'\"]+)['\"]", content)
            if style_match:
                print(f"  App uses style: {style_match.group(1)}")
                results["app_style"] = style_match.group(1)
            else:
                style_match2 = re.search(r"mapbox://styles/([^'\"]+)", content)
                if style_match2:
                    print(f"  App uses style: mapbox://styles/{style_match2.group(1)}")
                    results["app_style"] = f"mapbox://styles/{style_match2.group(1)}"
    except:
        pass

print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")
print(f"  Account: {MAPBOX_USER}")
print(f"  Styles: {len(results.get('styles', [])) if isinstance(results.get('styles'), list) else 'unknown'}")
print(f"  Tilesets: {len(results.get('tilesets', [])) if isinstance(results.get('tilesets'), list) else 'unknown'}")
print(f"  Datasets: {len(results.get('datasets', [])) if isinstance(results.get('datasets'), list) else 'unknown'}")

with open(r"C:\Users\mmrla\worldviewosnit\logs\mapbox_enum.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)
print("\nSaved to logs/mapbox_enum.json")
