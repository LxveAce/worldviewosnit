import urllib.request
import urllib.error
import ssl
import json
import socket
import time

ctx = ssl.create_default_context()
results = {}

# 1. Historical DNS via ViewDNS.info (no auth required)
print("=== ORIGIN IP DISCOVERY ===\n")

print("--- 1. DNS Resolution (current) ---")
try:
    ips = socket.getaddrinfo("worldviewosint.com", 443)
    unique = set()
    for family, kind, proto, canonname, sockaddr in ips:
        unique.add(sockaddr[0])
    for ip in sorted(unique):
        print(f"  {ip}")
    results["current_dns"] = list(unique)
except Exception as e:
    print(f"  Error: {e}")

# 2. Check for unproxied subdomains
print("\n--- 2. Subdomain DNS (looking for non-Cloudflare IPs) ---")
SUBDOMAINS = [
    "direct", "origin", "real", "backend", "api", "app",
    "mail", "mx", "smtp", "pop", "imap",
    "ftp", "sftp", "ssh",
    "cpanel", "webmail", "admin", "panel",
    "dev", "staging", "stage", "test", "beta", "demo",
    "db", "database", "mongo", "redis", "postgres",
    "cdn", "media", "static", "assets", "files",
    "ns1", "ns2", "dns1", "dns2",
    "vpn", "proxy", "gateway",
    "monitoring", "grafana", "prometheus", "kibana",
    "jenkins", "ci", "cd", "deploy",
    "git", "gitlab", "bitbucket",
    "ws", "websocket", "socket", "stream",
    "old", "legacy", "v1", "v2",
]

CLOUDFLARE_RANGES_PREFIX = ["104.16.", "104.17.", "104.18.", "104.19.", "104.20.", "104.21.",
                            "104.22.", "104.23.", "104.24.", "104.25.", "104.26.", "104.27.",
                            "172.64.", "172.65.", "172.66.", "172.67.", "172.68.", "172.69.",
                            "172.70.", "172.71.", "173.245.", "198.41.", "190.93.", "197.234.",
                            "188.114.", "162.158.", "141.101."]

def is_cloudflare(ip):
    return any(ip.startswith(prefix) for prefix in CLOUDFLARE_RANGES_PREFIX)

subdomain_results = {}
for sub in SUBDOMAINS:
    fqdn = f"{sub}.worldviewosint.com"
    try:
        ips = socket.getaddrinfo(fqdn, 443, socket.AF_INET)
        resolved = set(s[4][0] for s in ips)
        for ip in resolved:
            cf = is_cloudflare(ip)
            tag = "CLOUDFLARE" if cf else "[!!!] NON-CLOUDFLARE"
            print(f"  {fqdn:40} => {ip:18} {tag}")
            if not cf:
                subdomain_results[fqdn] = ip
    except socket.gaierror:
        pass
    except Exception as e:
        pass

if subdomain_results:
    print(f"\n  [!!!] POTENTIAL ORIGIN IPs FOUND:")
    for host, ip in subdomain_results.items():
        print(f"    {host} => {ip}")
else:
    print(f"\n  No non-Cloudflare subdomains found ({len(SUBDOMAINS)} tested)")

results["subdomain_scan"] = subdomain_results if subdomain_results else "none_found"

# 3. Check AAAA (IPv6) records
print("\n--- 3. IPv6 Records ---")
try:
    ips6 = socket.getaddrinfo("worldviewosint.com", 443, socket.AF_INET6)
    v6_set = set(s[4][0] for s in ips6)
    for ip in sorted(v6_set):
        print(f"  {ip}")
    results["ipv6"] = list(v6_set)
except socket.gaierror:
    print("  No AAAA records")
    results["ipv6"] = "none"

# 4. Fetch crt.sh for certificate history
print("\n--- 4. Certificate Transparency Logs (crt.sh) ---")
try:
    crt_url = "https://crt.sh/?q=%25.worldviewosint.com&output=json"
    req = urllib.request.Request(crt_url, headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req, timeout=30, context=ctx)
    certs = json.loads(resp.read().decode("utf-8"))
    print(f"  Found {len(certs)} certificate entries")

    seen_names = set()
    for cert in certs:
        name = cert.get("name_value", "")
        issuer = cert.get("issuer_name", "")
        not_before = cert.get("not_before", "")
        not_after = cert.get("not_after", "")
        if name not in seen_names:
            seen_names.add(name)
            print(f"  {name:40} | issued: {not_before[:10]} | issuer: {issuer[:50]}")

    results["ct_logs"] = {
        "total_entries": len(certs),
        "unique_names": list(seen_names),
        "certs": certs[:20]
    }
except Exception as e:
    print(f"  Error: {e}")
    results["ct_logs"] = {"error": str(e)}

# 5. Check Wayback Machine for pre-Cloudflare snapshots
print("\n--- 5. Wayback Machine ---")
try:
    wb_url = "https://web.archive.org/web/timemap/json?url=worldviewosint.com&matchType=prefix&limit=20"
    req = urllib.request.Request(wb_url, headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req, timeout=30, context=ctx)
    data = resp.read().decode("utf-8")
    if data.strip():
        snapshots = json.loads(data)
        print(f"  Found {len(snapshots)} snapshots")
        for snap in snapshots[:10]:
            if isinstance(snap, list) and len(snap) >= 2:
                print(f"  {snap[1]:20} | {snap[2] if len(snap) > 2 else ''}")
        results["wayback"] = snapshots[:20]
    else:
        print("  No snapshots found")
        results["wayback"] = "none"
except Exception as e:
    print(f"  Error: {e}")
    results["wayback"] = {"error": str(e)}

# 6. Check SecurityTrails-style DNS history via free APIs
print("\n--- 6. ViewDNS IP History ---")
try:
    vdns_url = "https://viewdns.info/iphistory/?domain=worldviewosint.com"
    req = urllib.request.Request(vdns_url, headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req, timeout=15, context=ctx)
    body = resp.read(50000).decode("utf-8", errors="replace")
    if "IP Address" in body and "<table" in body:
        import re
        ips_found = re.findall(r'(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})</td>', body)
        if ips_found:
            print(f"  Historical IPs found: {ips_found}")
            non_cf = [ip for ip in ips_found if not is_cloudflare(ip)]
            if non_cf:
                print(f"  [!!!] NON-CLOUDFLARE HISTORICAL IPs: {non_cf}")
            results["viewdns_history"] = {"all": ips_found, "non_cloudflare": non_cf}
        else:
            print("  No IPs found in response (may require premium)")
            results["viewdns_history"] = "no_ips_in_response"
    else:
        print("  Response did not contain expected data")
        results["viewdns_history"] = "unexpected_response"
except Exception as e:
    print(f"  Error: {e}")
    results["viewdns_history"] = {"error": str(e)}

# 7. SPF/DKIM/DMARC records (may leak origin IP)
print("\n--- 7. Email DNS Records (SPF/DKIM/DMARC) ---")
import subprocess
for rtype in ["TXT", "MX"]:
    try:
        result = subprocess.run(["nslookup", f"-type={rtype}", "worldviewosint.com"],
                               capture_output=True, text=True, timeout=10)
        output = result.stdout
        if "mail" in output.lower() or "v=spf" in output.lower() or "v=dmarc" in output.lower():
            print(f"  [{rtype}] {output.strip()}")
            results[f"dns_{rtype.lower()}"] = output.strip()
        else:
            print(f"  [{rtype}] No relevant records")
            results[f"dns_{rtype.lower()}"] = "none"
    except Exception as e:
        print(f"  [{rtype}] Error: {e}")

print(f"\n{'='*60}")
origin_candidates = []
if subdomain_results:
    origin_candidates.extend(subdomain_results.values())
if isinstance(results.get("viewdns_history"), dict) and results["viewdns_history"].get("non_cloudflare"):
    origin_candidates.extend(results["viewdns_history"]["non_cloudflare"])

if origin_candidates:
    print(f"ORIGIN IP CANDIDATES: {list(set(origin_candidates))}")
else:
    print("No origin IP candidates found — server is well-hidden behind Cloudflare")
print(f"{'='*60}")

with open(r"C:\Users\mmrla\worldviewosnit\logs\origin_ip_hunt.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2)
print("\nSaved to logs/origin_ip_hunt.json")
