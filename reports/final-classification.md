# Final System Classification

**Target:** https://worldviewosint.com
**Date:** 2026-05-21
**Classification Confidence:** HIGH

---

## Verdict: OPERATIONAL OSINT INTELLIGENCE DASHBOARD

This is a **real, operational, single-developer intelligence dashboard** that aggregates live data from multiple public and semi-public sources into a unified geospatial visualization. It is not a demo, not a clone, and not a surveillance tool.

---

## Evidence Summary

### What It IS

| Characteristic | Evidence |
|----------------|----------|
| **Operational system** | 53 days continuous uptime, live data feeds, 295MB active memory |
| **Real data** | Live ADS-B (180 military aircraft from adsb.lol), live AIS (269 vessels), live USGS earthquakes, live NASA FIRMS, live Binance BTC |
| **Single developer** | One Mapbox account (`juanes2794`), minimal frontend (single `app.js`), no build system, no team collaboration markers |
| **Personal project** | Portfolio/market tracking alongside OSINT, DeepSeek (budget AI), 6 AI calls/day limit (cost-conscious) |
| **Active maintenance** | Version progression (v3.2 → v3.4 → v6.0.0), deployed March 29, 2026 |
| **Multi-theater intelligence** | Covers Ukraine, Gaza, Sudan, Red Sea, Colombia, Americas — real geopolitical hotspots |
| **AI-augmented** | DeepSeek integration for automated intelligence briefings (currently disabled) |

### What It Is NOT

| Classification | Why Not |
|----------------|---------|
| **Demo/prototype** | Real data, real uptime, real AIS connection, real ADS-B feed |
| **Clone of known project** | Custom app.js (12KB), no framework scaffolding, no npm/package.json visible, unique data model |
| **Surveillance/tracking tool** | No automatic visitor data exfiltration, no analytics, no fingerprinting (only Cloudflare standard bot mgmt) |
| **Honeypot** | No special logging of visitor behavior, no honeytokens, standard application |
| **Commercial product** | No auth system (except Telegram), no user management, no pricing, no branding beyond "WORLDVIEW" |
| **Next.js/React app** | Vue 3 (CDN-loaded), Mapbox GL, raw JavaScript — no build system |

---

## Developer Profile (Inferred)

| Attribute | Evidence |
|-----------|----------|
| **Mapbox username** | `juanes2794` |
| **Language** | `<html lang="es">` — Spanish speaker (content is English) |
| **Interests** | OSINT, military intelligence, geopolitics, cryptocurrency (BTC tracking) |
| **Skill level** | Competent — Node.js backend with 5+ live data integrations, Mapbox globe, Vue.js frontend |
| **Budget-conscious** | DeepSeek (cheaper than OpenAI), 6 AI calls/day cap, Let's Encrypt + Cloudflare (free tier possible) |
| **Security awareness** | Telegram token server-side, auth on report endpoint; but missed API auth and Mapbox token restriction |

---

## Technology Assessment

### Sophistication: MODERATE-HIGH

| Aspect | Rating | Justification |
|--------|:------:|---------------|
| **Data integration** | High | 5 live real-time feeds + curated data, AIS decoding, ADS-B military filtering |
| **Frontend** | Moderate | Clean UI with Vue 3, but no build system, no component separation, single-file architecture |
| **Backend** | High | Custom Node.js server, 16 API endpoints, DeepSeek AI integration, Telegram bot, in-memory data store |
| **Infrastructure** | Moderate | Cloudflare CDN, good security headers, but no auth on data APIs |
| **Scalability** | Low | Single server, in-memory storage, no database, no caching layer |
| **Security** | Low-Moderate | Some good practices (HSTS, X-Frame-Options) but critical gaps (no API auth, no rate limiting) |

### Original vs. Assembled

**Verdict: ORIGINAL WORK**

- No matching open-source project found with this specific combination of features
- The code structure (single `app.js`, Vue 3 CDN, inline templates in HTML) is distinctive and not from any template
- The specific combination of data sources (adsb.lol + AIS + USGS + FIRMS + Binance + DeepSeek) is unique
- The conflict focus (Ukraine + Gaza + Sudan + Colombia) reflects a specific analytical perspective

---

## Key Metrics at Time of Analysis

| Metric | Value |
|--------|-------|
| Uptime | ~53 days (since ~March 29, 2026) |
| Memory | 295 MB |
| AIS vessels tracked | 269 |
| Military aircraft visible | 180 |
| Civilian aircraft | 0 (current snapshot) |
| Conflict zones | 36 |
| Disaster events | 18 |
| Risk level | 7.8/10 |
| Active fronts | 14 |
| Critical alerts | 5 |
| AI status | Disabled (0 calls today, max 6) |
| BTC/USDT | $77,206.52 |

---

## Open Questions

1. **Server-side Telegram behavior** — Does the server send automatic Telegram alerts beyond the user-triggered report? Cannot determine from client-side analysis alone.
2. **Data source for conflict/security/economic data** — Are these manually curated, AI-generated, or from an undisclosed API?
3. **Who is `juanes2794`?** — The Mapbox username suggests a personal identity, but no further OSINT on the developer was performed.
4. **Authentication mechanism** — The Telegram endpoint requires auth, but no login UI exists. How does authentication work? (Possible: IP whitelist, cookie-based, or server-side check)
5. **AIS data source** — The system tracks 269 vessels via AIS. Is this a direct radio receiver, an API, or a data sharing arrangement?

---

## Final Rating

| Category | Rating |
|----------|--------|
| **System Type** | Operational OSINT Dashboard |
| **Data Authenticity** | 5/10 streams verified REAL-TIME; 5/10 curated/aggregated |
| **Technical Sophistication** | Moderate-High (impressive for solo developer) |
| **Security Posture** | Medium-High risk (unauthenticated APIs, exposed tokens) |
| **Privacy Risk to Visitors** | Low (no custom tracking, only Cloudflare standard) |
| **Telegram Risk** | Low (auth-required, user-initiated, no auto-exfiltration) |
| **Classification Confidence** | HIGH |
