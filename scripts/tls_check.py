import ssl, socket, datetime

ctx = ssl.create_default_context()
with ctx.wrap_socket(socket.socket(), server_hostname="worldviewosint.com") as s:
    s.settimeout(10)
    s.connect(("worldviewosint.com", 443))
    cert = s.getpeercert()
    cipher = s.cipher()
    version = s.version()

lines = []
lines.append("=== TLS CERTIFICATE ANALYSIS: worldviewosint.com ===")
lines.append("Date: " + datetime.datetime.now().isoformat())
lines.append("TLS Version: " + str(version))
lines.append("Cipher Suite: " + str(cipher))
lines.append("")
lines.append("--- Subject ---")
for rdn in cert.get("subject", ()):
    for attr in rdn:
        lines.append("  " + attr[0] + ": " + attr[1])
lines.append("")
lines.append("--- Issuer ---")
for rdn in cert.get("issuer", ()):
    for attr in rdn:
        lines.append("  " + attr[0] + ": " + attr[1])
lines.append("")
lines.append("--- Validity ---")
lines.append("  Not Before: " + cert.get("notBefore", "N/A"))
lines.append("  Not After: " + cert.get("notAfter", "N/A"))
lines.append("")
lines.append("--- Subject Alternative Names ---")
sans = cert.get("subjectAltName", ())
for san_type, san_val in sans:
    lines.append("  " + san_type + ": " + san_val)
lines.append("")
lines.append("--- Serial Number ---")
lines.append("  " + cert.get("serialNumber", "N/A"))
lines.append("")
lines.append("--- OCSP ---")
for url in cert.get("OCSP", ()):
    lines.append("  " + url)
lines.append("")
lines.append("--- CA Issuers ---")
for url in cert.get("caIssuers", ()):
    lines.append("  " + url)
lines.append("")
lines.append("--- CRL Distribution Points ---")
for url in cert.get("crlDistributionPoints", ()):
    lines.append("  " + url)
lines.append("")
lines.append("--- Full Certificate Dict ---")
lines.append(str(cert))

with open(r"C:\Users\mmrla\worldviewosnit\recon\tls.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("TLS cert saved")
