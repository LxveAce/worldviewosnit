# API Map

**Target:** https://worldviewosint.com
**Date:** 2026-05-21
**Total endpoints discovered:** 16 real + SPA catch-all for everything else

---

## Real API Endpoints

### System

| Endpoint | Method | Auth | Response | Notes |
|----------|--------|:----:|----------|-------|
| `/api/health` | GET | No | `{"status":"OK","v":"6.0.0","up":4576493,"mem":"295MB","aisConnected":true,"aisVessels":269}` | Health check. Exposes version, uptime, memory, AIS status |
| `/api/risk-summary` | GET | No | Risk object with 11 fields | Aggregated risk score (7.8/10), alert counts, front counts |

### OSINT Data (all under `/api/osint/`)

| Endpoint | Method | Auth | Items | Data Shape | Source Classification |
|----------|--------|:----:|------:|------------|----------------------|
| `/api/osint/conflicts` | GET | No | 36 | `{lat,lon,name,type,intensity,description,region}` | AGGREGATED/CURATED |
| `/api/osint/thermal` | GET | No | 2 | `{lat,lon,brightness,confidence,frp,type,source,region,date}` | REAL-TIME (NASA FIRMS) |
| `/api/osint/oryx` | GET | No | 10 | `{lat,lon,side,equipment,status,count,evidence,region}` | AGGREGATED (Oryx project) |
| `/api/osint/maritime` | GET | No | 50 | `{id,mmsi,lat,lon,heading,speed,type,status,flag,class,shipType,timestamp}` | REAL-TIME (AIS feed) |
| `/api/osint/security` | GET | No | 10 | `{lat,lon,name,type,target,casualties,date,region}` | AGGREGATED/CURATED |
| `/api/osint/disasters` | GET | No | 18 | `{lat,lon,name,type,magnitude,status,date,region,tsunami,depth}` | REAL-TIME (USGS API) |
| `/api/osint/aviation` | GET | No | 180 mil, 0 civ | `{callsign,icao24,lat,lon,alt,vel,heading,country,on_ground,category,source,acType,reg,military}` | REAL-TIME (adsb.lol) |
| `/api/osint/losses` | GET | No | 3 sides | `{ru:{total,destroyed,captured,damaged},ua:{...},il:{...},lastUpdate}` | AGGREGATED (Oryx) |
| `/api/osint/economic` | GET | No | 10 | `{headline,impact,sector,region,sentiment}` | CURATED/SYNTHETIC |
| `/api/osint/infra` | GET | No | 10 | `{lat,lon,target,type,status,weapon,date,impact}` | CURATED |

### AI System

| Endpoint | Method | Auth | Response | Notes |
|----------|--------|:----:|----------|-------|
| `/api/ai/status` | GET | No | AI config object | Shows enabled:false, callsToday, callsMax(6), tokens, cost |
| `/api/ai/toggle` | POST | No* | Updated AI config | Toggles AI on/off. Body: `{enabled: bool}` |
| `/api/ai/force` | GET | No* | `{ok: bool, tokens: n, reason: str}` | Forces DeepSeek analysis run |

*AI endpoints appear unauthenticated but may have server-side rate limiting (max 6 calls/day).

### Telegram

| Endpoint | Method | Auth | Response | Notes |
|----------|--------|:----:|----------|-------|
| `/api/telegram/report` | GET | **YES (401)** | `{"error":"Authentication required"}` | Only authenticated users can trigger Telegram reports |

### Market

| Endpoint | Method | Auth | Response | Notes |
|----------|--------|:----:|----------|-------|
| `/api/portfolio` | GET | No | `{"market":{"asset":"BTC/USDT","price":"77206.52","status":"ACTIVE"}}` | Live Binance pricing |

---

## SPA Catch-All Behavior

All non-API paths return the same `index.html` (20,848 bytes). This includes:
- `/robots.txt`, `/sitemap.xml`, `/.well-known/*` — all return HTML, not their expected formats
- `/.env`, `/admin`, `/debug`, `/internal` — all return the SPA (not actual sensitive files)
- `/config.json`, `/manifest.json` — SPA, not real config files

**49 paths tested** — all returned identical HTML body except `/api/health` (JSON).

---

## Authentication Summary

| Category | Auth Required | Count |
|----------|:------------:|------:|
| OSINT data endpoints | No | 10 |
| System endpoints | No | 2 |
| AI endpoints | No (rate-limited) | 3 |
| Telegram | **Yes** | 1 |

**14 of 16 endpoints are completely unauthenticated.**

---

## Rate Limiting

- No `429 Too Many Requests` responses observed during probing
- No `X-RateLimit-*` headers in any response
- AI endpoints have application-level limiting (6 calls/day max)
- Cloudflare may provide DDoS-level rate limiting, but no API-level throttling was detected
