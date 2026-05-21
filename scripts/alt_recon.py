import urllib.request
import urllib.error
import ssl
import json
import time

ctx = ssl.create_default_context()
results = {}

def fetch(url, timeout=15):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        resp = urllib.request.urlopen(req, timeout=timeout, context=ctx)
        return resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as e:
        return f"HTTP {e.code}"
    except Exception as e:
        return f"ERROR: {e}"

# 1. CertSpotter (alternative to crt.sh)
print("=== 1. CERTSPOTTER CT LOGS ===")
certspotter_url = "https://api.certspotter.com/v1/issuances?domain=worldviewosint.com&include_subdomains=true&expand=dns_names"
data = fetch(certspotter_url)
try:
    certs = json.loads(data)
    if isinstance(certs, list):
        print(f"  Found {len(certs)} certificates")
        for cert in certs:
            dns_names = cert.get("dns_names", [])
            not_before = cert.get("not_before", "?")
            issuer = cert.get("issuer", {})
            issuer_name = issuer.get("name", "?") if isinstance(issuer, dict) else str(issuer)
            print(f"    DNS: {dns_names} | Issued: {not_before[:10]} | Issuer: {issuer_name[:50]}")
        results["certspotter"] = certs
    else:
        print(f"  Response: {data[:200]}")
        results["certspotter"] = data[:500]
except:
    print(f"  Response: {data[:200]}")
    results["certspotter"] = data[:500]

# 2. Google Transparency Report
print("\n=== 2. GOOGLE CT LOG SEARCH ===")
google_ct = f"https://transparencyreport.google.com/transparencyreport/api/v3/httpsreport/ct/certsearch?include_subdomains=true&domain=worldviewosint.com"
data = fetch(google_ct)
print(f"  Response: {data[:300]}")
results["google_ct"] = data[:1000]

# 3. Censys (free search, limited)
print("\n=== 3. CENSYS FREE SEARCH ===")
censys_url = "https://search.censys.io/api/v1/search/ipv4"
# Censys requires auth for API, but let's try the website search
print("  Censys API requires authentication — trying web search patterns")
print("  Recommended manual searches:")
print('    services.http.response.html_title:"WORLDVIEW OSINT"')
print('    services.http.response.body:"C4ISR v3.2"')
print('    services.http.response.body:"juanes2794"')
print('    services.tls.certificates.leaf_data.subject.common_name:"worldviewosint.com"')
results["censys"] = "requires_auth"

# 4. Shodan (free search via HTML scraping — limited)
print("\n=== 4. SHODAN SEARCH FINGERPRINTS ===")
shodan_queries = [
    'http.title:"WORLDVIEW OSINT"',
    'http.html:"C4ISR v3.2"',
    'http.html:"worldviewosint"',
    'ssl.cert.subject.cn:"worldviewosint.com"',
    'port:7474 neo4j',
]
print("  Shodan API requires key — recommended manual queries:")
for q in shodan_queries:
    print(f"    {q}")
results["shodan"] = {"queries": shodan_queries, "status": "requires_api_key"}

# 5. FOFA (Chinese search engine, free tier available)
print("\n=== 5. FOFA SEARCH ===")
fofa_queries = [
    'title="WORLDVIEW OSINT"',
    'body="C4ISR v3.2"',
    'body="worldviewosint"',
    'cert="worldviewosint.com"',
]
print("  FOFA search queries (manual):")
for q in fofa_queries:
    print(f"    {q}")
results["fofa"] = {"queries": fofa_queries}

# 6. URLScan.io (free, no auth needed for search)
print("\n=== 6. URLSCAN.IO ===")
urlscan_url = "https://urlscan.io/api/v1/search/?q=domain:worldviewosint.com"
data = fetch(urlscan_url)
try:
    urlscan = json.loads(data)
    total = urlscan.get("total", 0)
    scan_results = urlscan.get("results", [])
    print(f"  Found {total} scans")
    for r in scan_results[:5]:
        page = r.get("page", {})
        task = r.get("task", {})
        print(f"    {task.get('time','?')[:10]} | {page.get('url','?')} | IP: {page.get('ip','?')} | ASN: {page.get('asn','?')}")
    results["urlscan"] = urlscan
except:
    print(f"  Response: {data[:200]}")
    results["urlscan"] = data[:500]

# 7. DNSdumpster (free, no auth)
print("\n=== 7. ARCHIVE.ORG EARLIEST SNAPSHOT ===")
wb_avail = "https://archive.org/wayback/available?url=worldviewosint.com"
data = fetch(wb_avail)
try:
    wb = json.loads(data)
    snapshot = wb.get("archived_snapshots", {}).get("closest", {})
    if snapshot:
        print(f"  Closest snapshot: {snapshot.get('timestamp','?')} | URL: {snapshot.get('url','?')}")
    else:
        print("  No snapshots available")
    results["wayback_available"] = wb
except:
    print(f"  Response: {data[:200]}")
    results["wayback_available"] = data[:500]

# 8. SecurityTrails (check if free search works)
print("\n=== 8. SECURITYTRAILS FREE LOOKUP ===")
st_url = "https://api.securitytrails.com/v1/domain/worldviewosint.com"
st_headers = {"APIKEY": ""}  # Free tier requires key
print("  SecurityTrails requires API key for historical DNS")
print("  Free signup at: https://securitytrails.com/app/signup")
results["securitytrails"] = "requires_api_key"

# 9. Try to detect if the server reveals IP in error responses
print("\n=== 9. ERROR-BASED IP LEAK TESTING ===")

# Large payload
try:
    big_data = b"A" * 100000
    req = urllib.request.Request("https://worldviewosint.com/api/health",
        data=big_data, method="POST",
        headers={"User-Agent": "Mozilla/5.0", "Content-Type": "application/octet-stream"})
    resp = urllib.request.urlopen(req, timeout=10, context=ctx)
    body = resp.read(5000).decode("utf-8", errors="replace")
    print(f"  Large POST to /api/health: {resp.status} | {body[:100]}")
except urllib.error.HTTPError as e:
    body = ""
    try:
        body = e.read(5000).decode("utf-8", errors="replace")
    except:
        pass
    # Check for IP in error response
    import re
    ips = re.findall(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', body)
    if ips:
        print(f"  [!!!] IPs found in error response: {ips}")
    else:
        print(f"  Large POST error: {e.code} | {body[:100]}")
    results["error_ip_leak"] = {"status": e.code, "body": body[:500], "ips_found": ips}
except Exception as e:
    print(f"  Error: {e}")

# Invalid Host header
try:
    import http.client
    conn = http.client.HTTPSConnection("worldviewosint.com", context=ctx)
    conn.request("GET", "/api/health", headers={"Host": "evil.com", "User-Agent": "Mozilla/5.0"})
    resp = conn.getresponse()
    body = resp.read(5000).decode("utf-8", errors="replace")
    print(f"  Invalid Host header: {resp.status} | {body[:100]}")
    results["invalid_host"] = {"status": resp.status, "body": body[:500]}
    conn.close()
except Exception as e:
    print(f"  Invalid Host error: {e}")

print(f"\n{'='*60}")
print("SUMMARY")
print(f"{'='*60}")

with open(r"C:\Users\mmrla\worldviewosnit\logs\alt_recon.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)
print("Saved to logs/alt_recon.json")
