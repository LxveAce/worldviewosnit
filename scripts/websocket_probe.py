import socket
import ssl
import time
import json

TARGET_HOST = "worldviewosint.com"
TARGET_PORT = 443

WS_PATHS = [
    "/socket.io/?EIO=4&transport=websocket",
    "/socket.io/?EIO=3&transport=websocket",
    "/ws",
    "/websocket",
    "/live",
    "/stream",
    "/api/stream",
    "/api/ws",
    "/api/live",
    "/api/websocket",
    "/api/osint/stream",
    "/api/osint/ws",
    "/api/events",
    "/api/sse",
    "/realtime",
    "/feed",
]

results = []

def ws_handshake(path):
    ctx = ssl.create_default_context()
    sock = socket.create_connection((TARGET_HOST, TARGET_PORT), timeout=10)
    ssock = ctx.wrap_socket(sock, server_hostname=TARGET_HOST)

    key = "dGhlIHNhbXBsZSBub25jZQ=="
    request = (
        f"GET {path} HTTP/1.1\r\n"
        f"Host: {TARGET_HOST}\r\n"
        f"Upgrade: websocket\r\n"
        f"Connection: Upgrade\r\n"
        f"Sec-WebSocket-Key: {key}\r\n"
        f"Sec-WebSocket-Version: 13\r\n"
        f"Origin: https://{TARGET_HOST}\r\n"
        f"User-Agent: Mozilla/5.0\r\n"
        f"\r\n"
    )
    ssock.sendall(request.encode())
    response = ssock.recv(4096).decode("utf-8", errors="replace")
    ssock.close()
    return response

print("=== WebSocket Upgrade Probe ===\n")
print(f"{'Path':<50} {'Status':>6}  Response Summary")
print("-" * 100)

for path in WS_PATHS:
    try:
        resp = ws_handshake(path)
        first_line = resp.split("\r\n")[0] if resp else "(empty)"
        status = first_line.split(" ")[1] if " " in first_line else "???"

        is_upgrade = "101" in first_line
        is_html = "<!DOCTYPE" in resp or "<html" in resp
        has_ws_accept = "Sec-WebSocket-Accept" in resp

        if is_upgrade and has_ws_accept:
            tag = "[!!!] WEBSOCKET ACTIVE"
        elif is_upgrade:
            tag = "[!!!] 101 UPGRADE (no WS-Accept)"
        elif is_html:
            tag = "SPA catch-all"
        else:
            headers_preview = resp[:200].replace("\r\n", " | ")
            tag = headers_preview[:80]

        print(f"  {path:<48} {status:>6}  {tag}")
        results.append({
            "path": path,
            "status": status,
            "websocket": is_upgrade and has_ws_accept,
            "upgrade_101": is_upgrade,
            "spa_catchall": is_html,
            "first_line": first_line,
            "response_preview": resp[:500]
        })
    except Exception as e:
        print(f"  {path:<48}    ERR  {str(e)[:60]}")
        results.append({"path": path, "status": "ERROR", "error": str(e)[:200]})
    time.sleep(0.5)

ws_found = [r for r in results if r.get("websocket")]
upgrades = [r for r in results if r.get("upgrade_101")]

print(f"\n{'='*60}")
print(f"WebSocket endpoints found: {len(ws_found)}")
print(f"101 Upgrade responses: {len(upgrades)}")
print(f"Total tested: {len(results)}")
print(f"{'='*60}")

if ws_found:
    print("\n[!!!] ACTIVE WEBSOCKET ENDPOINTS:")
    for r in ws_found:
        print(f"  {r['path']}")

with open(r"C:\Users\mmrla\worldviewosnit\logs\websocket_probe.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print("\nSaved to logs/websocket_probe.json")
