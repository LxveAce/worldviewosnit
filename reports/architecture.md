# Architecture & Behavior Model

**Target:** https://worldviewosint.com
**Date:** 2026-05-21

---

## System Architecture Diagram

```
                            ┌─────────────────────────┐
                            │     EXTERNAL DATA        │
                            │      SOURCES             │
                            ├─────────────────────────┤
                            │  adsb.lol (ADS-B)       │
                            │  AIS Feed (Maritime)     │
                            │  USGS API (Earthquakes)  │
                            │  NASA FIRMS (Thermal)    │
                            │  Binance API (BTC)       │
                            │  DeepSeek API (AI)       │
                            │  OSINT Sources (Manual)  │
                            └───────────┬─────────────┘
                                        │
                                        ▼
┌──────────────────────────────────────────────────────────────┐
│                    ORIGIN SERVER (Node.js)                    │
│                     Version 6.0.0                            │
│                     Uptime: ~53 days                         │
│                     Memory: ~295MB                           │
├──────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌─────────────┐  ┌──────────────┐  ┌──────────────────┐   │
│  │ Data Ingest  │  │ API Router   │  │ AI Engine        │   │
│  │ Layer        │  │              │  │ (DeepSeek)       │   │
│  │             │  │ /api/osint/* │  │ /api/ai/*        │   │
│  │ - ADS-B poll│  │ /api/risk-*  │  │ Max 6 calls/day  │   │
│  │ - AIS feed  │  │ /api/portf.  │  │ Token tracking   │   │
│  │ - USGS poll │  │ /api/health  │  │ Cost tracking    │   │
│  │ - FIRMS poll│  │              │  │                  │   │
│  │ - Binance WS│  │              │  │                  │   │
│  └──────┬──────┘  └──────┬───────┘  └────────┬─────────┘   │
│         │                │                    │              │
│         ▼                │                    │              │
│  ┌─────────────┐         │           ┌────────▼─────────┐   │
│  │ Data Store  │◄────────┘           │ Telegram Bot     │   │
│  │ (in-memory) │                     │ /api/telegram/*  │   │
│  │             │                     │ Auth Required    │   │
│  │ 36 conflicts│                     │ Server-side only │   │
│  │ 50 vessels  │                     └──────────────────┘   │
│  │ 180 aircraft│                                            │
│  │ 18 disasters│         ┌──────────────────┐              │
│  │ 10 oryx     │         │ Static File      │              │
│  │ 10 security │         │ Server           │              │
│  │ 10 economic │         │                  │              │
│  │ 10 infra    │         │ index.html (20KB)│              │
│  │ 2 thermal   │         │ app.js (12KB)    │              │
│  └─────────────┘         │ SPA catch-all    │              │
│                          └──────────────────┘              │
└──────────────────────────┬───────────────────────────────────┘
                           │
                           ▼
              ┌────────────────────────┐
              │  CLOUDFLARE CDN/PROXY  │
              │  Atlanta PoP (ATL)     │
              │                        │
              │  - TLS termination     │
              │  - DDoS protection     │
              │  - Bot management      │
              │  - NEL reporting       │
              │  - cf-cache: DYNAMIC   │
              └───────────┬────────────┘
                          │
                          ▼
              ┌────────────────────────┐
              │    CLIENT BROWSER      │
              │                        │
              │  Vue 3 SPA             │
              │  Mapbox GL (Globe)     │
              │  Axios HTTP client     │
              │                        │
              │  Polls every 45s       │
              │  Aviation every 30s    │
              │  8 map layers          │
              └────────────────────────┘
```

---

## Data Lifecycle

### Real-Time Feeds

```
[adsb.lol API] ──poll──► [Server: parse + filter military] ──► /api/osint/aviation
[AIS Feed]     ──stream─► [Server: decode + store 269 vessels] ──► /api/osint/maritime  
[USGS API]     ──poll──► [Server: filter M2.5+] ──► /api/osint/disasters
[NASA FIRMS]   ──poll──► [Server: filter hotspots] ──► /api/osint/thermal
[Binance API]  ──WS/poll─► [Server: extract BTC/USDT] ──► /api/portfolio
```

### Curated Data

```
[Developer/AI] ──manual──► [Server: conflict zones DB] ──► /api/osint/conflicts (36 zones)
[Oryx project] ──manual──► [Server: losses DB] ──► /api/osint/oryx (10 items)
[OSINT reports]──manual──► [Server: security DB] ──► /api/osint/security (10 items)
[Unknown]      ──manual──► [Server: economic DB] ──► /api/osint/economic (10 items)
[OSINT reports]──manual──► [Server: infra DB] ──► /api/osint/infra (10 items)
```

### Aggregation

```
[All data streams] ──aggregate──► /api/risk-summary
  ├── totalRisk: 7.8/10
  ├── criticalAlerts: 5
  ├── activeFronts: 14
  ├── monitoredVessels: 8
  ├── thermalHotspots: 12
  ├── confirmedLosses: 21
  └── infraHits: 10
```

---

## UI → Network Relationship Map

| UI Element | User Action | Network Trigger | Endpoint | Interval |
|------------|-------------|-----------------|----------|----------|
| Page load | None (auto) | Initial data fetch | All endpoints | Once (3s delay) |
| Timer | None (auto) | Refresh all | All endpoints | Every 45s |
| Timer | None (auto) | Aviation refresh | `/api/osint/aviation` | Every 30s |
| Globe map | Mouse move | None | Client-side only | Continuous |
| Globe map | Click marker | Popup render | Client-side only | On click |
| Layer toggle | Click legend | Show/hide layer | Client-side only | On click |
| Nav button | Click (UKR, GAZA, etc.) | Map flyTo | Client-side only | On click |
| Sidebar tab | Click tab | None | Client-side only | On click |
| Sidebar item | Click conflict/vessel | Map flyTo | Client-side only | On click |
| AI BRIEF button | Click | Run analysis | `GET /api/ai/force` | On click |
| AI toggle | Click | Toggle AI | `POST /api/ai/toggle` | On click |
| TG REPORT button | Click | Send Telegram | `GET /api/telegram/report` | On click |

---

## Map Layer Configuration

| Layer ID | Color | Data Source | Marker Type | Label Zoom |
|----------|-------|-------------|-------------|:----------:|
| conflict | #ef4444 (red) | `/api/osint/conflicts` | Circle (r=5) + glow | 5+ |
| thermal | #f97316 (orange) | `/api/osint/thermal` | Circle (r=5) + glow | 5+ |
| aviation | #22d3ee (cyan) | `/api/osint/aviation` (civilian) | Circle (r=3) + glow | 5+ |
| maritime | #eab308 (yellow) | `/api/osint/maritime` | Circle (r=6) + glow | 5+ |
| security | #a855f7 (purple) | `/api/osint/security` | Circle (r=5) + glow | 5+ |
| oryx | #e2e8f0 (white) | `/api/osint/oryx` | Circle (r=5) + glow | 5+ |
| disaster | #22c55e (green) | `/api/osint/disasters` | Circle (r=5) + glow | 5+ |
| mil-aviation | #ff6b35 (orange) | `/api/osint/aviation` (military) | Circle (r=5) + glow | 5+ |

---

## Quick Navigation Presets

| Button | Center | Zoom | Theater |
|--------|--------|:----:|---------|
| GLOBAL | 10°N, 20°E | 2 | World overview |
| UKR | 48°N, 36.5°E | 6 | Ukraine conflict |
| GAZA | 31.38°N, 34.35°E | 10 | Gaza Strip |
| SUDAN | 15.5°N, 32.5°E | 6 | Sudan conflict |
| RED SEA | 14°N, 43°E | 6 | Houthi shipping lane |
| AMERICAS | 10°N, 75°W | 3.5 | Western hemisphere |
| COL | 4.5°N, 74°W | 6 | Colombia |

---

## Purpose Classification

Based on all evidence, this system is a **multi-source OSINT intelligence dashboard** with:

1. **Real-time geospatial monitoring** — live feeds from 5 external data sources
2. **Curated intelligence overlay** — manually maintained conflict/security/economic data
3. **AI-assisted analysis** — DeepSeek integration for automated briefings
4. **Report distribution** — Telegram bot for sharing intelligence summaries
5. **Market monitoring** — BTC/USDT price tracking (personal portfolio angle)
6. **Multi-theater focus** — Ukraine, Gaza, Sudan, Red Sea, Americas, Colombia
