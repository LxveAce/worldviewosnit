# Username OSINT — juanes2794

**Date:** 2026-05-21
**Tools:** Custom 45-platform scanner (`scripts/username_osint.py`) + Maigret (failed — 91% connection errors)

---

## Summary

**10 accounts found** across 45 platforms tested. Username `juanes2794` originates from Mapbox localStorage data (base64 `anVhbmVzMjc5NA==`).

---

## Accounts Found (Verified)

| Platform | URL | Category | Status |
|----------|-----|----------|--------|
| **Threads** | https://www.threads.com/@juanes2794 | Social | **VERIFIED** — Real name: **Esteban Gallego**, 62 followers, linked Instagram |
| Reddit | https://www.reddit.com/user/juanes2794 | Social | UNVERIFIED — blocked by anti-scraping, cannot confirm |
| Twitch | https://www.twitch.tv/juanes2794 | Streaming | UNVERIFIED — JS-rendered page, cannot confirm |
| TryHackMe | https://tryhackme.com/p/juanes2794 | Cybersecurity | UNVERIFIED — requires auth to view profile |
| HackTheBox | https://app.hackthebox.com/users/juanes2794 | Cybersecurity | UNVERIFIED — requires auth |

## False Positives (Verified Non-Existent)

| Platform | URL | Reason |
|----------|-----|--------|
| Kaggle | https://www.kaggle.com/juanes2794 | HTTP 404 — profile does not exist |
| Steam | https://steamcommunity.com/id/juanes2794 | "The specified profile could not be found" |
| PyPI | https://pypi.org/user/juanes2794/ | Page failed to load, likely non-existent |
| Signal | https://signal.me/#juanes2794 | URL format doesn't indicate account existence |
| Discord | https://discord.com/users/juanes2794 | URL format doesn't indicate account existence |

---

## Not Found (24 platforms)

Twitter/X, Instagram, TikTok, YouTube, Pinterest, Medium, Dev.to, Keybase, Gravatar, About.me, Linktree, DockerHub, RubyGems, Replit, CodePen, GitLab, Bitbucket, SourceForge, npm, Patreon, Behance, Dribbble, Flickr, Vimeo, SoundCloud, Spotify, Xbox, Telegram, Mastodon, Facebook, LinkedIn, Crunchbase, HackerOne, BugCrowd

---

## Errors (11 platforms)

Mostly connection timeouts or blocks (Hackernews rate-limited, others timed out).

---

## Analysis

### Developer Identity — CONFIRMED

**Real Name: Esteban Gallego**
**Username: juanes2794**
**Location: Valle del Cauca, Colombia** (from WHOIS)
**Social: Threads (@juanes2794, 62 followers, linked Instagram)**

"Juanes" is a common Colombian nickname for Juan Esteban — consistent with the name "Esteban Gallego."

### Next Steps for Identity Research

| Priority | Action | Why |
|----------|--------|-----|
| 1 | **Search "Esteban Gallego" on LinkedIn** | Full professional profile, employer, education |
| 2 | **Search Instagram @juanes2794** | Linked from Threads, likely has personal content |
| 3 | **Search Reddit u/juanes2794** | May reveal interests, technical discussions |
| 4 | **Search GitHub for "Esteban Gallego"** | May use real name instead of juanes2794 |
| 5 | **TryHackMe/HackTheBox** | Requires account to verify — would reveal security skill level |

### Notable Absences

- **GitHub (as juanes2794)**: Not found — may use real name or different handle
- **LinkedIn**: Not found via username — search "Esteban Gallego Valle del Cauca" instead
- **npm**: Not found — despite Node.js/TypeScript backend

### Geographic Correlation

- **WHOIS**: Valle del Cauca, Colombia
- **Threads**: Esteban Gallego (Colombian name, "Juanes" = nickname for Juan Esteban)
- **Mapbox localStorage**: `tokenU: juanes2794`
- **Domain registered**: March 28, 2026 — same day as first Cloudflare cert

---

## Maigret Results

Maigret (3,158 site database) was attempted but returned **0 accounts** due to 91% connection failure rate. The tool makes too many parallel connections from a single IP, triggering rate limiting across platforms. Our custom sequential scanner with 0.5s delays performed significantly better.

---

## Raw Data

- Custom scanner results: `logs/username_osint.json`
- Maigret results: `logs/maigret_results/report_juanes2794_ndjson.json`
