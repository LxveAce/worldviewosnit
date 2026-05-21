# Security Risk Assessment

**Target:** https://worldviewosint.com
**Date:** 2026-05-21

---

## Executive Summary

The application has a **mixed security posture**. Server-side security headers are well-configured (HSTS, X-Frame-Options DENY, nosniff). However, there are significant issues: an exposed Mapbox API token, completely unauthenticated data APIs, no API rate limiting, and AI control endpoints that anyone can toggle. The Telegram integration is properly secured (auth-required, server-side token).

---

## Findings

### CRITICAL

#### C1. Unauthenticated AI Control Endpoints
| Field | Detail |
|-------|--------|
| Endpoints | `POST /api/ai/toggle`, `GET /api/ai/force` |
| Risk | Anyone can enable/disable the AI system and trigger DeepSeek API calls |
| Impact | Cost abuse (DeepSeek API charges), denial of service for legitimate users |
| Evidence | `api.post('/api/ai/toggle',{enabled:n})` in app.js with no auth headers |
| CVSS Estimate | 7.5 (High) |

**Recommendation:** Add authentication to AI control endpoints immediately.

---

### HIGH

#### H1. All OSINT Data APIs Unauthenticated
| Field | Detail |
|-------|--------|
| Endpoints | All 10 `/api/osint/*` endpoints + `/api/risk-summary` + `/api/portfolio` |
| Risk | Data scraping, competitive intelligence harvesting, resource exhaustion |
| Impact | Backend load from automated scraping, AIS/aviation data redistribution |
| Evidence | All endpoints return full JSON without any authentication |
| CVSS Estimate | 5.3 (Medium) |

**Recommendation:** Implement API key authentication or session-based access control.

#### H2. Exposed Mapbox Access Token
| Field | Detail |
|-------|--------|
| Token | `[REDACTED — Mapbox public token, account: juanes2794]` |
| Account | `juanes2794` |
| Risk | Token abuse — anyone can use this token for Mapbox API requests, charged to the account |
| Impact | Financial (Mapbox billing), service disruption if token is revoked |
| Mitigation exists | Mapbox supports URL restriction on tokens — unclear if configured |
| CVSS Estimate | 5.3 (Medium) |

**Recommendation:** Restrict the Mapbox token to the `worldviewosint.com` domain in Mapbox account settings.

#### H3. No API Rate Limiting
| Field | Detail |
|-------|--------|
| Evidence | No `X-RateLimit-*` headers, no 429 responses during probing |
| Risk | Resource exhaustion, data harvesting at scale |
| Impact | Server overload, increased bandwidth costs, potential AIS/aviation source blocking |
| CVSS Estimate | 5.3 (Medium) |

**Recommendation:** Implement rate limiting (e.g., 60 requests/minute per IP).

---

### MEDIUM

#### M1. No Content Security Policy (CSP)
| Field | Detail |
|-------|--------|
| Evidence | No `Content-Security-Policy` header in response |
| Risk | XSS attacks could inject arbitrary scripts |
| Impact | Popup injection, data exfiltration via XSS, credential theft |
| Mitigation | X-XSS-Protection is set, but CSP is the modern standard |

**Recommendation:** Add CSP header restricting scripts to self + known CDNs.

#### M2. CORS Allows Credentials Without Origin Restriction
| Field | Detail |
|-------|--------|
| Header | `Access-Control-Allow-Credentials: true` |
| Missing | No `Access-Control-Allow-Origin` header observed |
| Risk | If the server reflects the Origin header, this enables CSRF-style API access |
| Impact | Cross-origin data theft from authenticated sessions |

**Recommendation:** Explicitly set `Access-Control-Allow-Origin` to `https://worldviewosint.com`.

#### M3. Server Version Information Disclosure
| Field | Detail |
|-------|--------|
| `/api/health` | Exposes: version (6.0.0), uptime, memory usage, AIS vessel count |
| Risk | Reconnaissance aid — attackers learn exact version, uptime, memory profile |
| Impact | Low direct impact, but assists targeted attacks |

**Recommendation:** Restrict `/api/health` to authenticated requests or internal IPs.

#### M4. Cloudflare Challenge Script (Bot Detection)
| Field | Detail |
|-------|--------|
| Evidence | Hidden iframe loading `/cdn-cgi/challenge-platform/scripts/jsd/main.js` |
| Purpose | Cloudflare bot detection / JavaScript challenge |
| Privacy | Runs fingerprinting code in a hidden iframe on every page load |
| Impact | Visitor fingerprinting for bot detection (standard Cloudflare behavior) |

**Note:** This is Cloudflare's bot management, not custom tracking by the site operator.

---

### LOW

#### L1. No robots.txt or sitemap.xml
| Evidence | Both paths return the SPA HTML, not actual robot/sitemap files |
| Impact | Search engines will index the SPA; no crawl guidance |

#### L2. HTML lang="es" Mismatch
| Evidence | `<html lang="es">` but all content is in English |
| Impact | Accessibility — screen readers will use Spanish pronunciation |

#### L3. No favicon.ico
| Evidence | `/favicon.ico` returns the SPA HTML |
| Impact | Browser tab shows generic icon; 404 noise in server logs |

---

## Privacy Assessment

### Visitor Tracking Inventory

| Technique | Present? | Source |
|-----------|:--------:|--------|
| Telegram auto-reporting | **No** | Telegram endpoint requires auth + user action |
| Google Analytics | **No** | No GA scripts found |
| Facebook Pixel | **No** | No FB scripts found |
| Hotjar / FullStory | **No** | No session recording scripts |
| Custom analytics | **No** | No analytics endpoints in app.js |
| Cookie tracking | **No** | No `set-cookie` headers observed |
| LocalStorage tracking | **Unknown** | Not observable without browser execution |
| Canvas fingerprinting | **No** | No canvas fingerprinting code in app.js |
| Cloudflare fingerprinting | **Yes** | Standard CF bot management (hidden iframe) |

### Privacy Compliance

| Requirement | Status |
|-------------|--------|
| Cookie consent banner | **Not present** |
| Privacy policy | **Not present** |
| GDPR compliance | **Not assessed** (no personal data collection observed) |
| CCPA compliance | **Not assessed** |

**Note:** Since no custom tracking or analytics are present (only Cloudflare's standard bot management), the privacy impact is minimal. However, the lack of a privacy policy is a gap if the site is publicly accessible.

---

## Risk Summary Matrix

| ID | Finding | Severity | CVSS | Status |
|----|---------|:--------:|:----:|--------|
| C1 | Unauthenticated AI control | CRITICAL | 7.5 | Open |
| H1 | Unauthenticated data APIs | HIGH | 5.3 | Open |
| H2 | Exposed Mapbox token | HIGH | 5.3 | Open |
| H3 | No API rate limiting | HIGH | 5.3 | Open |
| M1 | No CSP header | MEDIUM | 4.3 | Open |
| M2 | CORS credential misconfiguration | MEDIUM | 4.3 | Open |
| M3 | Health endpoint info disclosure | MEDIUM | 3.1 | Open |
| M4 | Cloudflare bot detection | MEDIUM | 2.1 | Expected |
| L1 | Missing robots.txt | LOW | 0.0 | Open |
| L2 | Language tag mismatch | LOW | 0.0 | Open |
| L3 | Missing favicon | LOW | 0.0 | Open |

---

## Overall Risk Rating: **MEDIUM-HIGH**

The system is an operational intelligence dashboard, not a malicious or surveillance tool. The main risks are around **access control** (anyone can access all data and control the AI system) and **token exposure** (Mapbox billing risk). The Telegram integration is the one properly secured component.
