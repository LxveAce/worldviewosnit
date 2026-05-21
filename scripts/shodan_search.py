import shodan
import json
import os
import sys
import time

API_KEY = os.environ.get("SHODAN_API_KEY", "")
if not API_KEY:
    print("[!] SHODAN_API_KEY not set")
    sys.exit(1)

api = shodan.Shodan(API_KEY)
results = {}

print("=== SHODAN ORIGIN IP DISCOVERY ===\n")

# 1. Account info
try:
    info = api.info()
    print(f"Account: scan_credits={info.get('scan_credits',0)} query_credits={info.get('query_credits',0)}")
    results["account"] = info
except Exception as e:
    print(f"Account info error: {e}")

# 2. Direct host lookup (Cloudflare IPs)
print("\n--- 1. Direct IP Lookup (Cloudflare) ---")
for ip in ["104.21.82.34", "172.67.193.202"]:
    try:
        host = api.host(ip)
        print(f"\n  {ip}:")
        print(f"    Org: {host.get('org', '?')}")
        print(f"    ISP: {host.get('isp', '?')}")
        print(f"    OS: {host.get('os', '?')}")
        print(f"    Ports: {host.get('ports', [])}")
        for svc in host.get("data", [])[:3]:
            print(f"    Port {svc.get('port')}: {svc.get('product', '?')} | {svc.get('data', '')[:100]}")
        results[f"host_{ip}"] = host
    except shodan.APIError as e:
        print(f"  {ip}: {e}")
        results[f"host_{ip}"] = str(e)

# 3. Search for the app by HTML content
print("\n--- 2. Content Fingerprint Searches ---")
QUERIES = [
    'http.title:"WORLDVIEW OSINT"',
    'http.html:"C4ISR v3.2"',
    'http.html:"worldviewosint"',
    'ssl.cert.subject.cn:"worldviewosint.com"',
    'http.html:"server.rugged"',
    'http.html:"worldview-osint"',
    'http.html:"aisConnected"',
    'port:7474 http.title:"Neo4j"',
]

for query in QUERIES:
    try:
        search = api.search(query)
        total = search.get("total", 0)
        print(f"\n  Query: {query}")
        print(f"  Results: {total}")

        if total > 0:
            for match in search.get("matches", [])[:5]:
                ip = match.get("ip_str", "?")
                port = match.get("port", "?")
                org = match.get("org", "?")
                product = match.get("product", "?")
                hostnames = match.get("hostnames", [])
                title = match.get("http", {}).get("title", "") if "http" in match else ""
                print(f"    [!!!] {ip}:{port} | {org} | {hostnames} | {product} | {title[:60]}")

        results[f"search_{query}"] = {
            "total": total,
            "matches": search.get("matches", [])[:10]
        }
        time.sleep(1)
    except shodan.APIError as e:
        print(f"  Query: {query} => Error: {e}")
        results[f"search_{query}"] = {"error": str(e)}
        time.sleep(1)

# 4. DNS lookup via Shodan
print("\n--- 3. Shodan DNS Resolve ---")
try:
    dns = api.dns.domain_info("worldviewosint.com")
    print(f"  Domain info: {json.dumps(dns, indent=2, default=str)[:500]}")
    results["dns_info"] = dns
except Exception as e:
    print(f"  DNS error: {e}")
    results["dns_info"] = str(e)

# 5. Reverse DNS on common hosting ranges
print("\n--- 4. SSL Certificate Search ---")
try:
    cert_search = api.search('ssl.cert.subject.cn:"worldviewosint.com"')
    total = cert_search.get("total", 0)
    print(f"  SSL cert matches: {total}")
    for match in cert_search.get("matches", [])[:10]:
        ip = match.get("ip_str", "?")
        port = match.get("port", "?")
        org = match.get("org", "?")
        hostnames = match.get("hostnames", [])
        ssl_cert = match.get("ssl", {}).get("cert", {})
        cn = ssl_cert.get("subject", {}).get("CN", "?") if ssl_cert else "?"
        print(f"    {ip}:{port} | {org} | CN={cn} | hostnames={hostnames}")
    results["ssl_cert_search"] = {
        "total": total,
        "matches": cert_search.get("matches", [])[:10]
    }
except shodan.APIError as e:
    print(f"  Error: {e}")
    results["ssl_cert_search"] = str(e)

# 6. Search for Neo4j instances that might be the backend
print("\n--- 5. Neo4j Instance Search ---")
neo4j_queries = [
    'port:7474 "neo4j" country:CO',
    'port:7687 country:CO',
    'port:7474 http.title:"Neo4j Browser"',
]
for query in neo4j_queries:
    try:
        search = api.search(query)
        total = search.get("total", 0)
        print(f"  {query} => {total} results")
        for match in search.get("matches", [])[:3]:
            ip = match.get("ip_str", "?")
            port = match.get("port", "?")
            org = match.get("org", "?")
            print(f"    {ip}:{port} | {org}")
        results[f"neo4j_{query}"] = {"total": total}
        time.sleep(1)
    except shodan.APIError as e:
        print(f"  {query} => Error: {e}")
        time.sleep(1)

print(f"\n{'='*60}")
origin_candidates = []
for key, val in results.items():
    if isinstance(val, dict) and "matches" in val:
        for match in val.get("matches", []):
            ip = match.get("ip_str", "")
            if ip and not any(ip.startswith(p) for p in ["104.16.", "104.17.", "104.18.", "104.19.",
                "104.20.", "104.21.", "104.22.", "104.23.", "104.24.", "104.25.", "104.26.", "104.27.",
                "172.64.", "172.65.", "172.66.", "172.67.", "172.68.", "172.69.", "172.70.", "172.71.",
                "173.245.", "198.41.", "190.93.", "197.234.", "188.114.", "162.158.", "141.101."]):
                origin_candidates.append(ip)

if origin_candidates:
    unique = list(set(origin_candidates))
    print(f"ORIGIN IP CANDIDATES: {unique}")
else:
    print("No origin IP candidates found via Shodan")
print(f"{'='*60}")

with open(r"C:\Users\mmrla\worldviewosnit\logs\shodan_search.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)
print("\nSaved to logs/shodan_search.json")
