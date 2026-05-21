import urllib.request
import urllib.error
import ssl
import json
import socket
import time

ctx = ssl.create_default_context()
results = {}

# 1. Retry crt.sh
print("=== CERTIFICATE TRANSPARENCY LOGS (crt.sh) ===\n")
for query in ["%25.worldviewosint.com", "worldviewosint.com"]:
    url = f"https://crt.sh/?q={query}&output=json"
    print(f"  Query: {query}")
    for attempt in range(3):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            resp = urllib.request.urlopen(req, timeout=30, context=ctx)
            certs = json.loads(resp.read().decode("utf-8"))
            print(f"  Found {len(certs)} certificate entries")

            seen = {}
            for cert in certs:
                name = cert.get("name_value", "")
                issuer = cert.get("issuer_name", "")
                not_before = cert.get("not_before", "")
                cert_id = cert.get("id", "")
                if name not in seen:
                    seen[name] = []
                seen[name].append({
                    "id": cert_id,
                    "issued": not_before,
                    "issuer": issuer,
                })

            for name, entries in sorted(seen.items()):
                print(f"    {name}")
                for e in entries[:3]:
                    print(f"      id={e['id']} issued={e['issued'][:10]} issuer={e['issuer'][:40]}")

            results[f"crt_{query}"] = {"total": len(certs), "unique_names": seen}
            break
        except Exception as e:
            print(f"  Attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(5)
    print()

# 2. Cloudflare alternative ports
print("=== CLOUDFLARE ALTERNATIVE PORT SCAN ===\n")
CF_HTTPS_PORTS = [443, 2053, 2083, 2087, 2096, 8443]
CF_HTTP_PORTS = [80, 8080, 8880, 2052, 2082, 2086, 2095]

port_results = {}

print("--- HTTPS ports ---")
for port in CF_HTTPS_PORTS:
    try:
        sock = socket.create_connection(("worldviewosint.com", port), timeout=5)
        ssock = ctx.wrap_socket(sock, server_hostname="worldviewosint.com")

        request = (
            f"GET /api/health HTTP/1.1\r\n"
            f"Host: worldviewosint.com\r\n"
            f"User-Agent: Mozilla/5.0\r\n"
            f"Accept: application/json\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )
        ssock.sendall(request.encode())
        response = ssock.recv(4096).decode("utf-8", errors="replace")
        ssock.close()

        first_line = response.split("\r\n")[0]
        is_json = '"status"' in response or '"version"' in response
        is_html = "<!DOCTYPE" in response
        preview = "JSON API" if is_json else "HTML" if is_html else response[:80]

        tag = " [DIFFERENT!]" if port != 443 and is_json else ""
        print(f"  {port:>5}/tcp OPEN  {first_line}  ({preview}){tag}")
        port_results[f"https_{port}"] = {"status": "open", "first_line": first_line, "api_responds": is_json}
    except socket.timeout:
        print(f"  {port:>5}/tcp TIMEOUT")
        port_results[f"https_{port}"] = {"status": "timeout"}
    except ConnectionRefusedError:
        print(f"  {port:>5}/tcp CLOSED")
        port_results[f"https_{port}"] = {"status": "closed"}
    except Exception as e:
        print(f"  {port:>5}/tcp ERROR: {str(e)[:60]}")
        port_results[f"https_{port}"] = {"status": "error", "error": str(e)[:200]}

print("\n--- HTTP ports ---")
for port in CF_HTTP_PORTS:
    try:
        sock = socket.create_connection(("worldviewosint.com", port), timeout=5)
        request = (
            f"GET /api/health HTTP/1.1\r\n"
            f"Host: worldviewosint.com\r\n"
            f"User-Agent: Mozilla/5.0\r\n"
            f"Accept: application/json\r\n"
            f"Connection: close\r\n"
            f"\r\n"
        )
        sock.sendall(request.encode())
        response = sock.recv(4096).decode("utf-8", errors="replace")
        sock.close()

        first_line = response.split("\r\n")[0]
        is_redirect = "301" in first_line or "302" in first_line or "307" in first_line
        is_json = '"status"' in response or '"version"' in response
        preview = "REDIRECT" if is_redirect else "JSON" if is_json else response[:60]

        print(f"  {port:>5}/tcp OPEN  {first_line}  ({preview})")
        port_results[f"http_{port}"] = {"status": "open", "first_line": first_line}
    except socket.timeout:
        print(f"  {port:>5}/tcp TIMEOUT")
        port_results[f"http_{port}"] = {"status": "timeout"}
    except ConnectionRefusedError:
        print(f"  {port:>5}/tcp CLOSED")
        port_results[f"http_{port}"] = {"status": "closed"}
    except Exception as e:
        print(f"  {port:>5}/tcp ERROR: {str(e)[:60]}")
        port_results[f"http_{port}"] = {"status": "error", "error": str(e)[:200]}

results["ports"] = port_results

# 3. Check for SSH/FTP on common ports via Cloudflare IPs
print("\n--- Non-HTTP ports (via Cloudflare IPs) ---")
OTHER_PORTS = [21, 22, 25, 110, 143, 993, 995, 3000, 3306, 5432, 6379, 8000, 8888, 9090]
for port in OTHER_PORTS:
    try:
        sock = socket.create_connection(("worldviewosint.com", port), timeout=3)
        banner = sock.recv(256).decode("utf-8", errors="replace")
        sock.close()
        print(f"  {port:>5}/tcp OPEN  banner: {banner[:80]}")
        port_results[f"other_{port}"] = {"status": "open", "banner": banner[:200]}
    except socket.timeout:
        port_results[f"other_{port}"] = {"status": "timeout"}
    except ConnectionRefusedError:
        port_results[f"other_{port}"] = {"status": "closed"}
    except Exception:
        port_results[f"other_{port}"] = {"status": "error"}

open_ports = [k for k, v in port_results.items() if v.get("status") == "open"]
print(f"\n{'='*60}")
print(f"Open ports: {len(open_ports)}")
for p in open_ports:
    print(f"  {p}")
print(f"{'='*60}")

with open(r"C:\Users\mmrla\worldviewosnit\logs\ct_and_ports.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)
print("\nSaved to logs/ct_and_ports.json")
