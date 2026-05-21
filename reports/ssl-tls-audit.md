# SSL/TLS Security Audit

**Target:** worldviewosint.com:443
**Date:** 2026-05-21
**Overall Grade:** A

---

## Protocol Support

| Protocol | Status | Note |
|----------|:------:|------|
| SSL 3.0 | DISABLED | POODLE safe |
| TLS 1.0 | DISABLED | BEAST safe |
| TLS 1.1 | DISABLED | Deprecated protocol |
| TLS 1.2 | ENABLED | ECDHE-ECDSA-CHACHA20-POLY1305 (256 bits) |
| TLS 1.3 | ENABLED | TLS_AES_256_GCM_SHA384 (256 bits) |

Only modern protocols enabled — excellent configuration.

## Certificate

| Field | Value |
|-------|-------|
| Subject CN | worldviewosint.com |
| Issuer | Let's Encrypt (E7) |
| Valid from | Mar 28 18:11:17 2026 |
| Valid until | Jun 26 18:11:16 2026 |
| SANs | `*.worldviewosint.com`, `worldviewosint.com` |
| Key type | ECDSA (from cipher name) |
| CA Issuers | http://e7.i.lencr.org/ |
| CRL | http://e7.c.lencr.org/26.crl |

Wildcard certificate — covers all subdomains. 90-day Let's Encrypt auto-renewal.

## Vulnerability Assessment

| Vulnerability | Status |
|--------------|:------:|
| POODLE (SSL 3.0) | **SAFE** — SSL 3.0 disabled |
| BEAST (TLS 1.0) | **SAFE** — TLS 1.0 disabled |
| FREAK/Logjam | **SAFE** — No export/weak ciphers |
| Heartbleed | N/A — requires deep probe (Cloudflare terminates TLS) |
| CRIME | **SAFE** — TLS compression not observed |

## Security Headers

| Header | Value | Assessment |
|--------|-------|:----------:|
| Strict-Transport-Security | `max-age=31536000` | GOOD (365 days) |
| X-Frame-Options | `DENY` | GOOD |
| X-Content-Type-Options | `nosniff` | GOOD |
| X-XSS-Protection | `1; mode=block` | PRESENT (deprecated) |
| Referrer-Policy | `strict-origin-when-cross-origin` | GOOD |
| Content-Security-Policy | NOT SET | **MISSING** |
| Permissions-Policy | NOT SET | **MISSING** |

## HSTS Analysis

| Property | Value | Required for Preload |
|----------|-------|:--------------------:|
| max-age | 31536000 (365 days) | >= 31536000 |
| includeSubDomains | **NOT SET** | Required |
| preload | **NOT SET** | Required |

**HSTS Preload: NOT ELIGIBLE** — missing `includeSubDomains` and `preload` directives.

## Findings

### Positive
- Only TLS 1.2 and 1.3 enabled — no legacy protocol support
- Strong cipher suites (ECDHE-ECDSA-CHACHA20-POLY1305, TLS_AES_256_GCM_SHA384)
- ECDSA key (better performance than RSA)
- HSTS enabled with 1-year max-age
- X-Frame-Options DENY prevents clickjacking
- Strict referrer policy

### Issues
1. **No CSP header** (MEDIUM) — allows XSS payload execution
2. **No Permissions-Policy** (LOW) — browser features not restricted
3. **HSTS not preload-eligible** (LOW) — first visit vulnerable to MITM downgrade
4. **X-XSS-Protection deprecated** (INFO) — CSP is the modern replacement

## Note on Cloudflare

TLS is terminated at Cloudflare's edge, not the origin server. This means:
- The TLS configuration is Cloudflare's, not the developer's
- Cloudflare manages cipher suites, protocols, and certificate rotation
- The origin server may use a different (potentially weaker) TLS configuration for the Cloudflare→origin connection
- Heartbleed testing against Cloudflare is meaningless — need the origin IP for direct testing
