import ssl
import socket
import json
import struct
import time

HOST = "worldviewosint.com"
PORT = 443
results = {}

print("=== SSL/TLS DEEP AUDIT ===\n")

# 1. Protocol version testing
print("--- Protocol Support ---")
PROTOCOLS = [
    ("SSL 3.0", ssl.PROTOCOL_TLS_CLIENT, ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2 | ssl.OP_NO_TLSv1_3),
    ("TLS 1.0", ssl.PROTOCOL_TLS_CLIENT, ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2 | ssl.OP_NO_TLSv1_3),
    ("TLS 1.1", ssl.PROTOCOL_TLS_CLIENT, ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_2 | ssl.OP_NO_TLSv1_3),
    ("TLS 1.2", ssl.PROTOCOL_TLS_CLIENT, ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_3),
    ("TLS 1.3", ssl.PROTOCOL_TLS_CLIENT, ssl.OP_NO_SSLv3 | ssl.OP_NO_TLSv1 | ssl.OP_NO_TLSv1_1 | ssl.OP_NO_TLSv1_2),
]

protocol_results = {}
for name, proto, opts in PROTOCOLS:
    try:
        ctx = ssl.SSLContext(proto)
        ctx.options |= opts
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.set_ciphers('ALL:@SECLEVEL=0')

        sock = socket.create_connection((HOST, PORT), timeout=10)
        ssock = ctx.wrap_socket(sock, server_hostname=HOST)
        version = ssock.version()
        cipher = ssock.cipher()

        tag = "[WEAK]" if name in ["SSL 3.0", "TLS 1.0", "TLS 1.1"] else "[OK]"
        print(f"  {name}: ENABLED {tag}")
        print(f"    Negotiated: {version}")
        print(f"    Cipher: {cipher[0]} ({cipher[2]} bits)")
        protocol_results[name] = {"enabled": True, "version": version, "cipher": cipher[0], "bits": cipher[2]}
        ssock.close()
    except ssl.SSLError as e:
        print(f"  {name}: DISABLED (good) - {str(e)[:60]}")
        protocol_results[name] = {"enabled": False}
    except Exception as e:
        print(f"  {name}: ERROR - {str(e)[:60]}")
        protocol_results[name] = {"error": str(e)[:200]}

results["protocols"] = protocol_results

# 2. Full cipher suite enumeration on best protocol
print("\n--- Cipher Suites (TLS 1.2 + 1.3) ---")
try:
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE

    sock = socket.create_connection((HOST, PORT), timeout=10)
    ssock = ctx.wrap_socket(sock, server_hostname=HOST)

    cipher = ssock.cipher()
    shared_ciphers = ssock.shared_ciphers()

    print(f"  Selected cipher: {cipher[0]} (protocol: {cipher[1]}, {cipher[2]} bits)")
    print(f"  Shared ciphers: {len(shared_ciphers)}")
    for c in shared_ciphers:
        print(f"    - {c[0]} ({c[1]}, {c[2]} bits)")

    results["ciphers"] = {
        "selected": {"name": cipher[0], "protocol": cipher[1], "bits": cipher[2]},
        "shared": [{"name": c[0], "protocol": c[1], "bits": c[2]} for c in shared_ciphers]
    }
    ssock.close()
except Exception as e:
    print(f"  Error: {e}")

# 3. Certificate details
print("\n--- Certificate Details ---")
try:
    ctx = ssl.create_default_context()
    sock = socket.create_connection((HOST, PORT), timeout=10)
    ssock = ctx.wrap_socket(sock, server_hostname=HOST)

    cert = ssock.getpeercert()
    cert_bin = ssock.getpeercert(binary_form=True)

    subject = dict(x[0] for x in cert.get("subject", ()))
    issuer = dict(x[0] for x in cert.get("issuer", ()))

    print(f"  Subject CN: {subject.get('commonName', '?')}")
    print(f"  Issuer: {issuer.get('organizationName', '?')} ({issuer.get('commonName', '?')})")
    print(f"  Not Before: {cert.get('notBefore', '?')}")
    print(f"  Not After: {cert.get('notAfter', '?')}")
    print(f"  Serial: {cert.get('serialNumber', '?')}")

    sans = cert.get("subjectAltName", ())
    san_list = [name for typ, name in sans if typ == "DNS"]
    print(f"  SANs: {san_list}")

    # OCSP
    print(f"  OCSP: {cert.get('OCSP', '?')}")
    print(f"  CA Issuers: {cert.get('caIssuers', '?')}")
    print(f"  CRL: {cert.get('crlDistributionPoints', '?')}")

    results["certificate"] = {
        "subject": subject,
        "issuer": issuer,
        "not_before": cert.get("notBefore"),
        "not_after": cert.get("notAfter"),
        "serial": cert.get("serialNumber"),
        "sans": san_list,
        "ocsp": cert.get("OCSP"),
        "size_bytes": len(cert_bin),
    }

    # Certificate chain
    print(f"\n  Certificate chain:")
    print(f"    [0] {subject.get('commonName', '?')}")
    print(f"    [1] {issuer.get('commonName', '?')}")

    ssock.close()
except Exception as e:
    print(f"  Error: {e}")

# 4. Check for known vulnerabilities manually
print("\n--- Vulnerability Assessment ---")

# Heartbleed (check for TLS 1.2 with specific extension)
print("  Heartbleed: N/A (requires raw TLS extension test)")
print("  POODLE: ", end="")
if protocol_results.get("SSL 3.0", {}).get("enabled"):
    print("[POTENTIALLY VULNERABLE] - SSL 3.0 enabled")
else:
    print("[SAFE] - SSL 3.0 disabled")

print("  BEAST: ", end="")
if protocol_results.get("TLS 1.0", {}).get("enabled"):
    print("[POTENTIALLY VULNERABLE] - TLS 1.0 enabled")
else:
    print("[SAFE] - TLS 1.0 disabled")

print("  FREAK/Logjam: ", end="")
weak_export = any("EXPORT" in c.get("name", "") or "DES" in c.get("name", "")
                   for c in results.get("ciphers", {}).get("shared", []))
if weak_export:
    print("[POTENTIALLY VULNERABLE] - Export/weak ciphers present")
else:
    print("[SAFE] - No export/weak ciphers")

# 5. HSTS check
print("\n--- HSTS Analysis ---")
try:
    import urllib.request
    ctx2 = ssl.create_default_context()
    req = urllib.request.Request(f"https://{HOST}/", headers={"User-Agent": "Mozilla/5.0"})
    resp = urllib.request.urlopen(req, timeout=10, context=ctx2)

    hsts = resp.headers.get("Strict-Transport-Security", "")
    xfo = resp.headers.get("X-Frame-Options", "")
    xcto = resp.headers.get("X-Content-Type-Options", "")
    csp = resp.headers.get("Content-Security-Policy", "")
    xxp = resp.headers.get("X-XSS-Protection", "")
    rp = resp.headers.get("Referrer-Policy", "")
    pp = resp.headers.get("Permissions-Policy", "")

    print(f"  HSTS: {hsts or 'NOT SET'}")
    print(f"  X-Frame-Options: {xfo or 'NOT SET'}")
    print(f"  X-Content-Type-Options: {xcto or 'NOT SET'}")
    print(f"  Content-Security-Policy: {csp or 'NOT SET'}")
    print(f"  X-XSS-Protection: {xxp or 'NOT SET'}")
    print(f"  Referrer-Policy: {rp or 'NOT SET'}")
    print(f"  Permissions-Policy: {pp or 'NOT SET'}")

    results["security_headers"] = {
        "hsts": hsts, "x_frame_options": xfo, "x_content_type_options": xcto,
        "csp": csp, "x_xss_protection": xxp, "referrer_policy": rp,
        "permissions_policy": pp,
    }

    # HSTS preload check
    if hsts:
        has_preload = "preload" in hsts.lower()
        has_subdomains = "includeSubDomains" in hsts
        max_age_match = None
        for part in hsts.split(";"):
            if "max-age" in part:
                try:
                    max_age_match = int(part.split("=")[1].strip())
                except:
                    pass
        print(f"\n  HSTS Analysis:")
        print(f"    max-age: {max_age_match} seconds ({max_age_match//86400 if max_age_match else 0} days)")
        print(f"    includeSubDomains: {has_subdomains}")
        print(f"    preload: {has_preload}")
        if max_age_match and max_age_match >= 31536000 and has_subdomains and has_preload:
            print(f"    Preload eligible: YES")
        elif max_age_match and max_age_match >= 31536000:
            print(f"    Preload eligible: NO (missing {'includeSubDomains' if not has_subdomains else ''} {'preload' if not has_preload else ''})")
except Exception as e:
    print(f"  Error: {e}")

# Summary
print(f"\n{'='*60}")
print("TLS AUDIT SUMMARY")
print(f"{'='*60}")

enabled_protos = [k for k, v in protocol_results.items() if v.get("enabled")]
print(f"  Enabled protocols: {enabled_protos}")
print(f"  Selected cipher: {results.get('ciphers', {}).get('selected', {}).get('name', '?')}")
print(f"  Key exchange bits: {results.get('ciphers', {}).get('selected', {}).get('bits', '?')}")

grade = "A"
if protocol_results.get("SSL 3.0", {}).get("enabled"):
    grade = "F"
elif protocol_results.get("TLS 1.0", {}).get("enabled"):
    grade = "B"
elif protocol_results.get("TLS 1.1", {}).get("enabled"):
    grade = "B"
elif not results.get("security_headers", {}).get("hsts"):
    grade = "A-"

print(f"  Estimated grade: {grade}")
results["grade"] = grade

with open(r"C:\Users\mmrla\worldviewosnit\logs\ssl_audit.json", "w", encoding="utf-8") as f:
    json.dump(results, f, indent=2, default=str)
print("\nSaved to logs/ssl_audit.json")
