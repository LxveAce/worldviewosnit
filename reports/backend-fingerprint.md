# Backend Fingerprint Report

**Target:** https://worldviewosint.com
**Date:** 2026-05-21
**Analyst:** Automated OSINT Lab

---

## Confirmed Technology Stack

### Frontend
| Component | Version | Evidence |
|-----------|---------|----------|
| **Vue.js 3** | Production build | CDN-loaded from `unpkg.com/vue@3/dist/vue.global.prod.js` |
| **Mapbox GL JS** | v3.1.2 | CSS + JS loaded from `api.mapbox.com`; globe projection with terrain |
| **Axios** | Latest (CDN) | HTTP client from `cdn.jsdelivr.net/npm/axios/dist/axios.min.js` |
| **Google Fonts** | N/A | JetBrains Mono (monospace) + Orbitron (display) |
| **No build system** | N/A | Raw `app.js` (12,410 bytes), no Webpack/Vite, no source maps, no `.map` files |

### Backend
| Component | Version | Evidence |
|-----------|---------|----------|
| **Node.js** | Unknown | Memory reporting in `/api/health` (295MB — typical Node.js heap), uptime in seconds |
| **Custom HTTP server** | v6.0.0 | Version from `/api/health` response; no `x-powered-by` header (Express/Fastify would set this) |
| **DeepSeek AI** | Unknown | AI tab labeled "DeepSeek"; `/api/ai/status` + `/api/ai/force` endpoints |
| **AIS receiver/aggregator** | Live | `aisConnected: true`, tracking 269 vessels, real MMSI data |

### Infrastructure
| Component | Evidence |
|-----------|----------|
| **Cloudflare CDN/Proxy** | `Server: cloudflare`, `CF-RAY: 9ff37bcbca8d0d1f-ATL`, NEL reporting |
| **Cloudflare DNS** | NS: `melody.ns.cloudflare.com`, `tosana.ns.cloudflare.com` |
| **Let's Encrypt TLS** | Issuer: `E7`, wildcard cert `*.worldviewosint.com` |
| **TLS 1.3** | Cipher: `TLS_AES_256_GCM_SHA384` (256-bit) |
| **NOT Vercel** | No `x-vercel-id` header |
| **NOT Next.js** | No `/_next/` paths, no `__NEXT_DATA__`, no `x-nextjs-cache` |

### Mapbox Account
| Field | Value |
|-------|-------|
| Username | `juanes2794` |
| Token | `[REDACTED — Mapbox public token, account: juanes2794]` |
| Map Style | `mapbox://styles/mapbox/dark-v11` |
| Features | Globe projection, 3D terrain (1.5x exaggeration), fog/atmosphere, DEM tiles |

## Server Behavior

### Response Headers
```
HTTP/1.1 200 OK
Server: cloudflare
CF-RAY: 9ff37bcbca8d0d1f-ATL (Atlanta PoP)
cf-cache-status: DYNAMIC
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
X-XSS-Protection: 1; mode=block
Strict-Transport-Security: max-age=31536000
Referrer-Policy: strict-origin-when-cross-origin
Access-Control-Allow-Credentials: true
Cache-Control: public, max-age=0
Last-Modified: Sun, 29 Mar 2026 13:04:08 GMT
```

### Hosting Model
- **Serverless:** No — persistent Node.js process with 53-day uptime
- **Traditional server:** Yes — long-running process behind Cloudflare
- **Caching:** None (`max-age=0`), all API responses are DYNAMIC at Cloudflare edge
- **Deployment date:** ~March 29, 2026 (matches `Last-Modified` and uptime calculation)

### Polling Behavior
| Interval | Endpoint(s) |
|----------|-------------|
| 45 seconds | All data endpoints (`refreshAll()`) |
| 30 seconds | Aviation only (`fetchAviation()`) |
| 1 second | Clock update (client-side only) |
| Initial delay | 3 seconds after page load |

### SPA Routing
- Server returns the same `index.html` for ALL non-API paths (SPA catch-all)
- Only `/api/*` paths return distinct responses
- No `robots.txt`, `sitemap.xml`, or `manifest.json` — all return the SPA HTML

## Version Discrepancies

| Location | Version |
|----------|---------|
| HTML `<title>` | C4ISR v3.2 |
| JavaScript console log | WORLDVIEW v3.4 |
| `/api/health` response | 6.0.0 |

Three different version numbers across three locations — indicates version strings are updated independently and not from a single source of truth.

## Architecture Summary

```
[Cloudflare CDN/Proxy — Atlanta PoP]
  ↓ (HTTPS termination, DDoS protection, NEL)
[Origin Server — Node.js (custom, no framework headers)]
  ├── Static: index.html + app.js (SPA catch-all)
  ├── /api/osint/* — OSINT data endpoints (12 routes)
  ├── /api/ai/* — DeepSeek integration (3 routes)
  ├── /api/telegram/* — Telegram reporting (auth-protected)
  ├── /api/portfolio — Binance market data
  └── /api/risk-summary — Aggregated risk score
  ↓
[External Data Sources]
  ├── adsb.lol — ADS-B aviation data
  ├── AIS feed — Maritime vessel tracking (269 vessels)
  ├── USGS — Earthquake data
  ├── NASA FIRMS — Thermal hotspots
  ├── Binance — BTC/USDT pricing
  ├── DeepSeek — AI analysis
  └── Telegram Bot API — Report delivery
```
