# Data Authenticity Report

**Target:** https://worldviewosint.com
**Date:** 2026-05-21

---

## Summary

The system ingests data from a mix of **real-time APIs**, **curated/aggregated OSINT**, and **potentially AI-generated content**. The core data streams (aviation, maritime, earthquakes) are verifiably real. Geopolitical and economic data appears curated or synthesized.

---

## Classification by Data Stream

### 1. Aviation — REAL-TIME API
**Confidence: HIGH**

| Evidence | Detail |
|----------|--------|
| Source attribution | `"source": "adsb.lol"` — real ADS-B data aggregator |
| Real callsigns | HUSK99 (USAF prefix), JANET77/JANET24 (EG&G Area 51 flights) |
| Real registrations | N365SR — confirmed JANET fleet Boeing 737-600 |
| Real ICAO hex codes | `c2b3c3`, `a4207f`, `a2b320` — valid format |
| Real coordinates | JANET flights over Nevada desert (36.59°N, 116.05°W) |
| Live data | 180 military aircraft, positions update every 30 seconds |
| Category codes | Category 7 = military (OpenSky convention) |

**Verdict:** Live ADS-B data from adsb.lol. Real military aircraft being tracked in real-time.

---

### 2. Maritime — REAL-TIME API
**Confidence: HIGH**

| Evidence | Detail |
|----------|--------|
| Real MMSI numbers | 477995030 (Hong Kong flag), 367473510 (US flag), 319084700 (Cayman Islands) |
| Valid MMSI prefixes | 477=Hong Kong, 367=US, 319=Cayman — all correct MID codes |
| Heading 511 | Standard AIS "not available" value |
| Live AIS connection | `aisConnected: true`, 269 vessels in backend, 50 served to client |
| Real coordinates | Hong Kong harbor (22.29°N, 114.17°E), Charleston SC (32.85°N, 79.95°W) |
| Unix timestamps | `1775803404906` — valid millisecond timestamp |

**Verdict:** Live AIS data feed. Real vessels with valid MMSI numbers, following AIS protocol conventions.

---

### 3. Disasters (Earthquakes) — REAL-TIME API
**Confidence: HIGH**

| Evidence | Detail |
|----------|--------|
| USGS format | Place names follow USGS convention: "X km DIRECTION of CITY, STATE" |
| Today's data | All events dated 2026-05-21 |
| Real locations | Bandar Abbas Iran (M4.9), Valdez Alaska (M2.5), South Sandwich Islands (M4.7) |
| Correct field structure | `magnitude`, `depth`, `tsunami` flag — matches USGS GeoJSON API |
| Plausible values | Depths range 1-128 km, magnitudes 2.5-4.9 — realistic distribution |

**Verdict:** Real-time USGS earthquake API data. Format and content are unmistakably from the USGS GeoJSON feed.

---

### 4. Market Data — REAL-TIME API
**Confidence: HIGH**

| Evidence | Detail |
|----------|--------|
| Asset format | `"BTC/USDT"` — Binance trading pair format |
| Price format | `"77206.52000000"` — 8 decimal places, Binance API format |
| Endpoint name | `/api/portfolio` — suggests personal investment tracking |

**Verdict:** Live Binance API data. Price format is characteristic of Binance REST API.

---

### 5. Thermal (FIRMS) — REAL-TIME API
**Confidence: HIGH**

| Evidence | Detail |
|----------|--------|
| Field names | `brightness`, `confidence`, `frp` (Fire Radiative Power) — NASA FIRMS fields |
| Source attribution | `source` field present |
| Low count | Only 2 hotspots — realistic for filtered/thresholded data |

**Verdict:** NASA FIRMS (Fire Information for Resource Management System) data.

---

### 6. Conflicts — AGGREGATED/CURATED
**Confidence: MEDIUM**

| Evidence | Detail |
|----------|--------|
| Real locations | Avdiivka, Bakhmut-Chasiv Yar, Zaporizhzhia, Kherson — all real frontline sectors |
| Accurate coordinates | 48.14°N, 37.74°E for Avdiivka — correct |
| No source attribution | No API source, no timestamps, no URLs |
| Static feel | 36 zones, descriptions are general ("Mechanized assault, heavy RU losses") |
| Includes multiple theaters | Ukraine (14+), Gaza (5+), Sudan (3+), Colombia (2+), Myanmar, Haiti |

**Verdict:** Curated from OSINT sources (ISW, DeepState Map, open-source reporting). Not from a single API. Updated periodically by the developer or an AI pipeline.

---

### 7. Oryx Losses — AGGREGATED
**Confidence: MEDIUM**

| Evidence | Detail |
|----------|--------|
| Real equipment types | Referenced in losses (not shown in sample but field exists) |
| Side tracking | RU: 16 total (15D/1C), UA: 2 (2DMG), IL: 3 (1D/2DMG) |
| Low numbers | Total of 21 losses tracked — this is a subset, not the full Oryx database |
| `evidence` field | Suggests links to visual confirmation (Oryx methodology) |

**Verdict:** Aggregated from the Oryx project or similar OSINT loss tracking. Subset, not comprehensive.

---

### 8. Economic Intelligence — CURATED/SYNTHETIC
**Confidence: LOW-MEDIUM**

| Evidence | Detail |
|----------|--------|
| No source URLs | No links to original articles |
| Too clean | All headlines are perfectly formatted, consistent structure |
| Plausible content | "EU approves 14th sanctions package" — real policy area but unverifiable |
| Specific numbers | "LMT +4.2%, RTX +3.8%" — could be real or fabricated |
| No timestamps | No publication dates, no source attribution |

**Verdict:** Possibly AI-generated summaries of real economic trends, or manually curated. Cannot confirm from an external API source.

---

### 9. Infrastructure Targets — CURATED
**Confidence: MEDIUM**

| Evidence | Detail |
|----------|--------|
| Real targets | Kyiv Power Grid, Odesa Port Terminal, Tatarstan Refinery — all real infrastructure |
| Real weapons | Shahed-136, Iskander-M, Kalibr, Kh-101 — real Russian/Iranian weapon systems |
| Stale dates | All from March 2026 (2 months old) |
| Specific impacts | "200k affected", "Supply route cut" — detailed but unverifiable |
| Multi-theater | Ukraine, Russia, Gaza, Sudan, Colombia, Haiti |

**Verdict:** Curated from open-source conflict reporting. Accurate in general but not machine-updated.

---

### 10. Security Incidents — CURATED
**Confidence: MEDIUM**

| Evidence | Detail |
|----------|--------|
| 10 incidents | Fixed number suggests manual curation |
| Fields present | name, type, target, casualties, date, region |

**Verdict:** Curated from OSINT reporting. Not from a real-time API.

---

## Overall Data Authenticity Matrix

| Stream | Source | Classification | Confidence | Update Frequency |
|--------|--------|---------------|:----------:|-----------------|
| Aviation | adsb.lol | **REAL-TIME** | HIGH | 30s |
| Maritime | AIS feed | **REAL-TIME** | HIGH | 45s |
| Earthquakes | USGS API | **REAL-TIME** | HIGH | 45s |
| Thermal | NASA FIRMS | **REAL-TIME** | HIGH | 45s |
| Market | Binance API | **REAL-TIME** | HIGH | 45s |
| Conflicts | OSINT curation | **AGGREGATED** | MED | Manual/periodic |
| Oryx losses | Oryx project | **AGGREGATED** | MED | Manual/periodic |
| Infrastructure | OSINT curation | **CURATED** | MED | Stale (March 2026) |
| Security | OSINT curation | **CURATED** | MED | Unknown |
| Economic | Unknown | **CURATED/SYNTHETIC** | LOW-MED | Unknown |

---

## Conclusion

**5 of 10 data streams are verifiably real-time**, pulling from established public APIs (adsb.lol, USGS, NASA FIRMS, AIS, Binance). The remaining 5 are curated/aggregated from OSINT sources, with economic data being the least verifiable. The system is **not a demo** — it processes real data with real-time feeds. However, the geopolitical intelligence layer appears to be manually maintained or AI-assisted rather than fully automated.
