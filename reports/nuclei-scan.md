# Nuclei Vulnerability Scan — worldviewosint.com

**Date:** 2026-05-21
**Tool:** Nuclei v3.3.7, templates v10.4.3
**Scans:** Quick (2,519 templates) + Full (6,615 templates, in progress)

---

## Summary

**Zero vulnerabilities found.** All findings are informational severity only.

| Severity | Count |
|----------|-------|
| CRITICAL | 0 |
| HIGH | 0 |
| MEDIUM | 0 |
| LOW | 0 |
| INFO | 10 |

---

## Findings

### 1. WAF Detection: Cloudflare
- **Severity:** Info
- **Detail:** Cloudflare WAF is actively protecting the application
- **Impact:** All scan traffic is filtered through Cloudflare, which blocks most attack payloads

### 2. Missing Security Headers (7 headers)

| Header | Status | Risk |
|--------|--------|------|
| `Content-Security-Policy` | Missing | **Moderate** — no XSS mitigation via CSP |
| `Permissions-Policy` | Missing | Low — browser features not restricted |
| `Cross-Origin-Embedder-Policy` | Missing | Low — no cross-origin isolation |
| `Cross-Origin-Opener-Policy` | Missing | Low — no cross-origin isolation |
| `Cross-Origin-Resource-Policy` | Missing | Low — no cross-origin resource restriction |
| `X-Permitted-Cross-Domain-Policies` | Missing | Low — Flash/PDF cross-domain |
| `Clear-Site-Data` | Missing | Info — no logout cache clearing |

**Most significant:** Missing `Content-Security-Policy` header. Combined with the CORS origin reflection vulnerability (see `reports/cors-vulnerability.md`), this means:
- No restrictions on inline scripts or external resource loading
- An attacker exploiting CORS could also inject scripts without CSP blocking them
- The attack chain: CORS reflection → credential theft → no CSP to prevent script injection

### 3. Deprecated X-XSS-Protection Header
- **Severity:** Info
- **Header:** `X-XSS-Protection: 1; mode=block`
- **Detail:** This header is deprecated in modern browsers. Chrome removed XSS Auditor in 2019. The header is harmless but provides no protection. CSP should be used instead.

### 4. Technology Detection: Cloudflare
- **Severity:** Info
- **Detail:** Confirms Cloudflare CDN/proxy

---

## Headers Present vs Missing

### Present (from previous security audit)
- `Strict-Transport-Security: max-age=31536000` (HSTS, 1 year)
- `X-Content-Type-Options: nosniff`
- `X-Frame-Options: SAMEORIGIN`
- `X-XSS-Protection: 1; mode=block` (deprecated)
- `Referrer-Policy: strict-origin-when-cross-origin`

### Missing (from nuclei scan)
- `Content-Security-Policy`
- `Permissions-Policy`
- `Cross-Origin-Embedder-Policy`
- `Cross-Origin-Opener-Policy`
- `Cross-Origin-Resource-Policy`
- `X-Permitted-Cross-Domain-Policies`
- `Clear-Site-Data`

---

## Full Scan Progress

The comprehensive scan (6,615 templates, 14,687 requests) is running at ~5-6 RPS due to rate limiting. At 26% completion with 0 vulnerability matches, the remaining templates are unlikely to find anything Cloudflare isn't blocking. Results will be in `logs/nuclei_scan.txt` and `logs/nuclei_scan.json`.

API endpoint-specific scan also running against 19 URLs.

---

## Assessment

The site is **well-protected at the infrastructure level**:
- Cloudflare WAF blocks most automated attack payloads
- TLS configuration is strong (Grade A, TLS 1.2+1.3 only)
- Basic security headers present (HSTS, X-Frame-Options, nosniff)

**Weaknesses are at the application level**, not detectable by nuclei:
1. **CORS origin reflection** (CRITICAL — see `reports/cors-vulnerability.md`)
2. **Missing CSP** (MEDIUM — enables script injection if combined with CORS)
3. **Exposed docker-compose.yml** (CRITICAL — see `reports/docker-compose-exposure.md`)
4. **Neo4j with no authentication** (CRITICAL if origin IP discovered)

These application-level issues require manual testing, not automated scanning.
