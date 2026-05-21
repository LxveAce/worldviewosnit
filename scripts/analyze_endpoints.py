import json

with open(r"C:\Users\mmrla\worldviewosnit\logs\endpoints.json") as f:
    data = json.load(f)

seen = {}
for entry in data:
    preview = entry.get("body_preview", "")[:200]
    if preview not in seen:
        seen[preview] = []
    seen[preview].append(entry["path"])

print(f"Unique response bodies: {len(seen)}")
print()
for i, (preview, paths) in enumerate(seen.items()):
    print(f"--- Body variant {i+1} ({len(paths)} paths) ---")
    print(f"Paths: {', '.join(paths[:10])}")
    if len(paths) > 10:
        print(f"  ... and {len(paths)-10} more")
    print(f"Preview: {preview[:200]}")
    print()

# Also check specific interesting paths
interesting = ["/robots.txt", "/.env", "/api", "/config.json", "/manifest.json", "/favicon.ico"]
for path in interesting:
    for entry in data:
        if entry["path"] == path:
            print(f"=== {path} ===")
            print(f"Content-Type: {entry.get('content_type', 'N/A')}")
            print(f"Body: {entry.get('body_preview', 'N/A')[:300]}")
            print()
