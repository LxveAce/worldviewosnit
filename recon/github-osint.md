# GitHub OSINT Research Report
**Date:** 2026-05-21
**Target:** worldviewosint.com / Mapbox username "juanes2794"

---

## PART 1: Developer Reconnaissance - "juanes2794"

### GitHub Profile Search

**Direct Profile URL:** `https://github.com/juanes2794`
- **Result: 404 - Profile does NOT exist on GitHub**
- The username "juanes2794" does not have a GitHub account

### Variation Searches
| Username Searched | Platform | Result |
|---|---|---|
| juanes2794 | GitHub | 404 - Not found |
| juanes-2794 | GitHub | No results |
| juanes_2794 | GitHub | No results |
| juanes2794 | GitLab | No results |
| juanes2794 | Bitbucket | No results |
| juanes2794 | npm | No results |
| juanes2794 | StackOverflow | No results |

### Cross-Platform Search Results
- **Mapbox:** Username "juanes2794" is used on Mapbox (confirmed via worldviewosint.com source code analysis), but Mapbox profiles are not publicly searchable/indexable
- **GitHub:** No account exists. The developer either uses a different GitHub username or hosts code privately
- **No code repositories, gists, or public activity found anywhere under this username**

### Similar GitHub Usernames Found (NOT confirmed matches)
- `juan794` (Juan Guarnizo) - different person
- `juanesrp` - different person
- `Juanses` - different person
- `juanset` (Juan Sebastian Espinosa) - different person

### Assessment
The developer of worldviewosint.com uses "juanes2794" exclusively as a Mapbox username but does NOT use it on GitHub or other major developer platforms. This suggests either:
1. They use a completely different username on GitHub/code platforms
2. They host code privately (private repos, self-hosted Git)
3. The site is built using Mapbox Studio without traditional version control
4. The developer intentionally compartmentalizes identities across platforms

**This is a dead end for GitHub-based reconnaissance on this specific username.**

---

## PART 2: OSINT & Security Tools for Web App Analysis

### Target Profile
- **Site:** worldviewosint.com
- **Frontend:** Vue.js
- **Backend:** Node.js
- **Mapping:** Mapbox GL JS
- **CDN/WAF:** Cloudflare
- **APIs:** Unauthenticated endpoints detected
- **Data feeds:** AIS maritime, ADS-B aviation, RSS, WebSocket

---

### CATEGORY 1: OSINT Reconnaissance Frameworks

#### 1. SpiderFoot
- **URL:** https://github.com/smicallef/spiderfoot
- **Stars:** 17,900
- **Language:** Python
- **Last Release:** v4.0 (April 2022)
- **Commits:** 3,742
- **What it does:** Automates OSINT for threat intelligence and attack surface mapping. 200+ modules for DNS, WHOIS, email, social media, dark web, IP geolocation, and more.
- **Relevance to target:** HIGH - Can enumerate all infrastructure behind worldviewosint.com, discover related domains, email addresses, linked services, Mapbox API usage patterns, and more. Web UI makes it accessible.
- **Maintenance:** Last official release is 2022, but still widely used. Community active.

#### 2. OWASP Amass
- **URL:** https://github.com/owasp-amass/amass
- **Stars:** 14,600
- **Language:** Go
- **Last Updated:** April 17, 2026
- **What it does:** In-depth attack surface mapping and asset discovery. Subdomain enumeration, DNS resolution, network mapping, WHOIS lookups, certificate transparency log analysis.
- **Relevance to target:** HIGH - Essential for discovering all subdomains, related infrastructure, DNS records, and certificate history of worldviewosint.com. Can find dev/staging environments.
- **Maintenance:** Actively maintained through 2026.

#### 3. GoSearch
- **URL:** https://github.com/ibnaleem/gosearch
- **Stars:** 3,400
- **Language:** Go
- **Last Updated:** May 20, 2026
- **What it does:** Searches digital footprint across 300+ websites for a given username.
- **Relevance to target:** MEDIUM - Could search "juanes2794" across platforms to find additional developer accounts not found via manual search.
- **Maintenance:** Very actively maintained.

#### 4. Tookie OSINT
- **URL:** https://github.com/Alfredredbird/tookie-osint
- **Stars:** 2,200
- **Language:** Python
- **Last Updated:** April 24, 2026
- **What it does:** Advanced OSINT information gathering tool that finds social media accounts based on inputs.
- **Relevance to target:** MEDIUM - Useful for tracing the developer's other accounts from the "juanes2794" handle.
- **Maintenance:** Active.

---

### CATEGORY 2: Web Application Penetration Testing

#### 5. Nuclei
- **URL:** https://github.com/projectdiscovery/nuclei
- **Stars:** 28,800
- **Language:** Go
- **Last Release:** v3.8.0 (April 18, 2026)
- **Commits:** 6,329
- **What it does:** Fast, template-based vulnerability scanner. YAML-based DSL for custom vulnerability detection. Covers CVEs, misconfigurations, exposed panels, default credentials, API vulnerabilities, and more. 10,000+ community templates.
- **Relevance to target:** CRITICAL - Can scan worldviewosint.com for known vulnerabilities in Vue.js, Node.js, Mapbox misconfigurations, exposed API endpoints, information disclosure, and more. Template-based approach means new checks are constantly added.
- **Maintenance:** Extremely active. Industry standard.

#### 6. Katana
- **URL:** https://github.com/projectdiscovery/katana
- **Stars:** 16,700
- **Language:** Go
- **Last Release:** v1.6.1 (May 5, 2026)
- **Commits:** 1,580
- **What it does:** Next-generation web crawler/spider. Headless and non-headless modes. JavaScript rendering support. Extracts endpoints, forms, APIs, and parameters from web applications.
- **Relevance to target:** CRITICAL - Can crawl worldviewosint.com with full JS rendering (essential for Vue.js SPA), discover all API endpoints, WebSocket connections, hidden routes, and Mapbox API calls. Headless mode bypasses JS-rendering requirements.
- **Maintenance:** Very actively maintained.

#### 7. Subfinder
- **URL:** https://github.com/projectdiscovery/subfinder
- **Stars:** 13,700
- **Language:** Go
- **Last Release:** v2.14.0 (April 27, 2026)
- **Commits:** 2,201
- **What it does:** Fast passive subdomain enumeration. Uses passive online sources only (no active probing). Integrates with dozens of DNS/certificate databases.
- **Relevance to target:** HIGH - Will discover all subdomains of worldviewosint.com including API servers, staging environments, admin panels, and other infrastructure that may not be behind Cloudflare.
- **Maintenance:** Very actively maintained.

#### 8. httpx
- **URL:** https://github.com/projectdiscovery/httpx
- **Stars:** 10,000
- **Language:** Go
- **Last Release:** v1.9.0 (March 9, 2026)
- **Commits:** 2,768
- **What it does:** Fast multi-purpose HTTP toolkit. Probes hosts for tech stack, status codes, titles, content length, headers, TLS info, and more. Smart HTTPS/HTTP fallback.
- **Relevance to target:** HIGH - Can probe all discovered hosts/subdomains to fingerprint technology, identify server headers, detect Cloudflare presence (or absence), and map the full web infrastructure.
- **Maintenance:** Very actively maintained.

#### 9. OWASP Nettacker
- **URL:** https://github.com/OWASP/Nettacker
- **Stars:** ~3,500
- **Language:** Python
- **What it does:** Automated penetration testing framework. Port scanning, service detection, subdomain enumeration, vulnerability scanning, credential brute-forcing.
- **Relevance to target:** MEDIUM - General-purpose scanner, less specialized than Nuclei but broader in scope.
- **Maintenance:** Active OWASP project.

---

### CATEGORY 3: Cloudflare Origin IP Discovery

#### 10. CloakQuest3r
- **URL:** https://github.com/spyboy-productions/CloakQuest3r
- **Stars:** 2,100
- **Language:** Python
- **Commits:** 83
- **What it does:** Identifies origin IP exposure of websites behind Cloudflare. Uses subdomain scanning, IP address history via ViewDNS, SSL certificate analysis, and optional SecurityTrails API integration.
- **Relevance to target:** CRITICAL - Directly applicable. If worldviewosint.com has ANY origin IP exposure (misconfigured DNS, leaked via email headers, historical DNS records, exposed subdomains), this tool will find it.
- **Maintenance:** Active. Featured in KitPloit "Top 20 Hacking Tools 2023."

#### 11. CloudFlair
- **URL:** https://github.com/christophetd/CloudFlair
- **Stars:** 3,000
- **Language:** Python
- **Commits:** 37
- **What it does:** Uses Censys internet-wide scan data to find origin servers. Searches for SSL certificates matching the target domain, then tests candidate IPs for matching content.
- **Relevance to target:** MEDIUM - Powerful technique but requires paid Censys API access (free tier removed late 2024). Still useful if you have Censys access.
- **Maintenance:** Limited. No recent updates. Censys API change reduced utility.

#### 12. Cloudmare
- **URL:** https://github.com/mrh0wl/Cloudmare
- **Stars:** 1,800
- **Language:** Python
- **Commits:** 108
- **What it does:** Finds origin servers behind Cloudflare, Sucuri, or Incapsula via misconfigured DNS. Uses subdomain brute-forcing and multiple verification methods.
- **Relevance to target:** LOW - Repository archived January 2026. No longer maintained.
- **Maintenance:** ARCHIVED - Read-only.

#### 13. Bypasser
- **URL:** https://github.com/0xR4bbit/bypasser
- **Stars:** ~500
- **Language:** Python
- **What it does:** Real IP Discovery Tool to bypass Cloudflare/WAF (v2.3). Multiple detection techniques.
- **Relevance to target:** MEDIUM - Active alternative to CloudFlair.
- **Maintenance:** Active.

---

### CATEGORY 4: API Security Testing

#### 14. Akto
- **URL:** https://github.com/akto-api-security/akto
- **Stars:** 1,500
- **Language:** Java/JavaScript/Vue
- **Last Release:** v2.2.2 (May 2026)
- **Commits:** 12,561
- **What it does:** Proactive API security platform. API discovery, security posture assessment, CI/CD testing, 1000+ built-in tests covering OWASP Top 10 and HackerOne Top 10 (BOLA, auth bypass, SSRF, XSS). Supports traffic capture from Burp Suite, AWS, Postman.
- **Relevance to target:** HIGH - Directly applicable to testing worldviewosint.com's unauthenticated APIs. Can detect BOLA (broken object-level authorization), missing authentication, data exposure, and injection flaws. Vue.js frontend is same tech as target.
- **Maintenance:** Extremely active. 1,298 releases.

#### 15. VulnAPI
- **URL:** https://github.com/cerberauth/vulnapi
- **Stars:** 265
- **Language:** Go
- **Last Release:** v0.9.0 (April 14, 2026)
- **Commits:** 515
- **What it does:** DAST tool for API security. Scans via CLI or OpenAPI contracts. JWT testing, GraphQL testing, technology fingerprinting, CVSS scoring, OWASP classification.
- **Relevance to target:** MEDIUM - Useful for targeted API testing. Lower star count but actively developed and focused specifically on API vulnerabilities.
- **Maintenance:** Active.

#### 16. API Security Checklist
- **URL:** https://github.com/shieldfy/API-Security-Checklist
- **Stars:** ~23,000
- **Language:** Documentation
- **What it does:** Comprehensive checklist of security countermeasures for API design, testing, and release. Covers authentication, JWT, OAuth, access control, input validation, processing, output, CI/CD.
- **Relevance to target:** HIGH - Reference guide for systematically auditing worldviewosint.com's API security posture.
- **Maintenance:** Reference document, stable.

---

### CATEGORY 5: JavaScript Analysis & Secret Discovery

#### 17. LinkFinder
- **URL:** https://github.com/GerbenJavado/LinkFinder
- **Stars:** 4,400
- **Language:** Python
- **Commits:** 168
- **What it does:** Finds endpoints and their parameters in JavaScript files using jsbeautifier and regex analysis. Outputs HTML or plaintext reports.
- **Relevance to target:** CRITICAL - Vue.js SPAs bundle all API endpoints, route definitions, and configuration into JavaScript files. LinkFinder will extract every API endpoint, WebSocket URL, Mapbox API key, and internal route from worldviewosint.com's JS bundles.
- **Maintenance:** Stable, widely used in bug bounty community.

#### 18. SecretFinder
- **URL:** https://github.com/m4ll0k/SecretFinder
- **Stars:** 2,200
- **Language:** Python
- **What it does:** Discovers sensitive data (API keys, access tokens, JWTs, OAuth tokens, AWS keys, Google API keys, etc.) in JavaScript files. Based on LinkFinder with expanded regex patterns. Also available as Burp Suite extension.
- **Relevance to target:** CRITICAL - Will find any exposed Mapbox API tokens, backend API keys, authentication tokens, or other secrets embedded in worldviewosint.com's JavaScript bundles. Essential for Vue.js apps which often embed API configuration in client-side code.
- **Maintenance:** Stable.

#### 19. JSFScan.sh
- **URL:** https://github.com/KathanP19/JSFScan.sh
- **Stars:** ~1,000
- **Language:** Bash
- **What it does:** All-in-one JavaScript recon automation. Combines endpoint extraction, secret detection, variable name extraction, and JS file collection into a single workflow.
- **Relevance to target:** HIGH - Automates the entire JS analysis pipeline for worldviewosint.com. Wraps LinkFinder, SecretFinder, and other tools.
- **Maintenance:** Active.

#### 20. JShunter
- **URL:** https://github.com/cc1a2b/JShunter
- **Stars:** ~500
- **Language:** Go
- **What it does:** Analyzes JavaScript files and extracts endpoints, API paths, and potential security vulnerabilities. CLI tool optimized for speed.
- **Relevance to target:** MEDIUM - Go-based alternative to LinkFinder. Faster on large JS bundles.
- **Maintenance:** Active.

#### 21. NodeJSScan
- **URL:** https://github.com/ajinabraham/nodejsscan
- **Stars:** 2,600
- **Language:** Python
- **What it does:** Static security code scanner for Node.js applications. Detects SQL injection, XSS, command injection, insecure file operations, hardcoded secrets, and more.
- **Relevance to target:** HIGH - If source code is obtained, this is the go-to scanner for Node.js backend vulnerabilities. Even analyzing exposed JS bundles can yield results.
- **Maintenance:** Active.

---

### CATEGORY 6: AIS Maritime Tracking OSINT

#### 22. PhantomTide
- **URL:** https://github.com/tg12/phantomtide
- **Stars:** 95
- **Language:** Python/JavaScript
- **Release:** v1.79.0
- **Commits:** 111
- **What it does:** Global maritime intelligence platform. Real-time vessel tracking, AIS data analysis, sanctions monitoring, shipping routes, port activity, anomaly detection, multi-source convergence scoring. Ranks overlapping data sources rather than treating each equally.
- **Relevance to target:** HIGH - worldviewosint.com appears to use AIS data feeds. PhantomTide shows how professional maritime OSINT platforms are built and can be used as a reference/comparison for understanding worldviewosint.com's maritime capabilities and data sources.
- **Maintenance:** Active development with regular releases.

#### 23. Aegis OSINT Map
- **URL:** https://github.com/FNBIP/aegis-osint-map
- **Stars:** 8
- **Language:** TypeScript (98.6%)
- **Commits:** 37
- **What it does:** Real-time OSINT situational awareness platform on a 3D Mapbox globe. Features submarine cables, pipelines, military bases, live flights (OpenSky), ship tracking (AIS), CCTV feeds, country instability index, intel dossiers, decentralized chat (Nostr).
- **Relevance to target:** HIGH - Uses Mapbox GL JS (same as worldviewosint.com). Demonstrates similar architecture patterns. Shows how AIS/ADS-B data is integrated into Mapbox-based platforms. Can inform understanding of worldviewosint.com's architecture.
- **Maintenance:** Moderate activity.

#### 24. Atlas Bear OSINT Tools
- **URL:** https://github.com/atlas-bear/osint-tools
- **Stars:** ~200
- **Language:** Documentation/Tools list
- **What it does:** Maritime and supply chain OSINT tools curated for intelligence practitioners. Lists AIS tracking services, container tracking, port intelligence sources.
- **Relevance to target:** MEDIUM - Reference for understanding data sources worldviewosint.com might use.
- **Maintenance:** Active curation.

---

### CATEGORY 7: ADS-B Military Aircraft Tracking

#### 25. IRONSIGHT
- **URL:** https://github.com/NoblerWorks-HQ/IRONSIGHT
- **Stars:** 256
- **Language:** TypeScript (97.9%)
- **Commits:** 31
- **What it does:** Real-time OSINT command center. Military aircraft tracking via adsb.lol, missile/strike tracker, regional threat monitor, naval tracker, satellite thermal detection (NASA FIRMS), prediction markets, energy markets. 50+ data sources. All free, no API keys needed.
- **Relevance to target:** HIGH - Uses similar architecture to worldviewosint.com (Next.js/TypeScript, Leaflet maps, real-time data feeds). Shows how ADS-B military tracking is implemented. All data sources are free and documented.
- **Maintenance:** Active.

#### 26. Skytrack
- **URL:** https://github.com/ANG13T/skytrack
- **Stars:** 524
- **Language:** Python
- **Commits:** 89
- **What it does:** CLI planespotting and aircraft OSINT tool. Accepts tail numbers or ICAO designators, retrieves intelligence from FlightAware, OpenSky API, and aviation databases. Generates PDF reports. Converts between tail/ICAO formats.
- **Relevance to target:** MEDIUM - Focused on individual aircraft lookup rather than real-time tracking. Useful for investigating specific aircraft spotted on worldviewosint.com.
- **Maintenance:** Moderate.

#### 27. WingID
- **URL:** https://github.com/SilverHaze99/WingID
- **Stars:** ~50
- **Language:** Desktop application
- **What it does:** Military aircraft identification and intelligence gathering. Searchable database of military aircraft with specifications, operational info, and visual identification aids. Uses only unclassified public sources.
- **Relevance to target:** LOW - Reference database, not a tracking tool. Useful for identifying aircraft types seen on worldviewosint.com.
- **Maintenance:** Active.

#### 28. OSINT War Room
- **URL:** https://github.com/Hue-Jhan/OSINT-War-Room
- **Stars:** 39
- **Language:** JavaScript
- **Commits:** 8
- **What it does:** Tactical dashboard for tracking global conflicts and military movements in real-time. Live air/naval radar, Telegram intelligence scraping, GDELT conflict events, news aggregation, CCTV feeds, VIX fear index.
- **Relevance to target:** MEDIUM - Similar concept to worldviewosint.com. Shows data source integration patterns.
- **Maintenance:** Early stage.

#### 29. awesome-adsb
- **URL:** https://github.com/rickstaa/awesome-adsb
- **Stars:** ~500
- **Language:** Documentation
- **What it does:** Curated list of ADS-B tools, SDR projects, feeders, decoders, and tracking resources.
- **Relevance to target:** HIGH - Reference for understanding all ADS-B data sources and tools. Essential for understanding what data feeds worldviewosint.com could be using.
- **Maintenance:** Active curation.

---

## RECOMMENDED TOOL PIPELINE FOR TARGET ANALYSIS

### Phase 1: Infrastructure Discovery
```
1. subfinder -d worldviewosint.com -all       # Find all subdomains
2. httpx -l subdomains.txt -tech-detect       # Fingerprint all hosts
3. amass enum -d worldviewosint.com           # Deep asset discovery
```

### Phase 2: Cloudflare Bypass
```
4. python3 CloakQuest3r.py worldviewosint.com # Find origin IP
5. python3 CloudFlair.py worldviewosint.com   # Censys-based search (needs API)
```

### Phase 3: JavaScript Analysis (Vue.js SPA)
```
6. katana -u worldviewosint.com -jc -headless # Crawl with JS rendering
7. python3 LinkFinder.py -i target_js -o cli  # Extract all API endpoints
8. python3 SecretFinder.py -i target_js -o cli # Find exposed secrets/tokens
```

### Phase 4: API Security Testing
```
9. nuclei -u worldviewosint.com -t api/       # Scan for API vulns
10. akto - import discovered endpoints         # Full API security audit
```

### Phase 5: Vulnerability Assessment
```
11. nuclei -u worldviewosint.com -severity critical,high  # CVE scanning
12. nuclei -u worldviewosint.com -t exposed-panels/       # Find admin panels
13. nuclei -u worldviewosint.com -t misconfiguration/     # Config issues
```

---

## PRIORITY TOOLS (Top 10 for This Target)

| Priority | Tool | Why |
|---|---|---|
| 1 | **Nuclei** (28.8k stars) | Most comprehensive vuln scanner, Vue.js/Node.js templates |
| 2 | **Katana** (16.7k stars) | JS-rendering crawler essential for Vue.js SPA |
| 3 | **LinkFinder** (4.4k stars) | Extract every API endpoint from JS bundles |
| 4 | **SecretFinder** (2.2k stars) | Find Mapbox tokens, API keys in JS |
| 5 | **CloakQuest3r** (2.1k stars) | Bypass Cloudflare, find origin IP |
| 6 | **Subfinder** (13.7k stars) | Discover all subdomains |
| 7 | **httpx** (10k stars) | Fingerprint all discovered hosts |
| 8 | **Amass** (14.6k stars) | Deep infrastructure mapping |
| 9 | **SpiderFoot** (17.9k stars) | Full OSINT automation |
| 10 | **Akto** (1.5k stars) | Dedicated API security testing |

---

## KEY FINDINGS SUMMARY

### Developer ("juanes2794")
- GitHub account does NOT exist under this username
- No presence found on GitHub, GitLab, Bitbucket, npm, or StackOverflow
- Username is only confirmed on Mapbox
- Recommend using GoSearch or Tookie OSINT to enumerate this username across 300+ platforms

### Target Infrastructure
- Vue.js + Node.js + Mapbox + Cloudflare is a well-understood attack surface
- Unauthenticated APIs are the highest-priority vulnerability class
- Vue.js SPAs expose significant information in JavaScript bundles (endpoints, tokens, routes)
- Cloudflare bypass tools exist and are actively maintained
- AIS/ADS-B data integration patterns are well-documented in open-source projects

### Tool Ecosystem
- ProjectDiscovery suite (Nuclei, Katana, Subfinder, httpx) is the most actively maintained and comprehensive toolset
- All recommended tools are free and open source
- Most tools had commits within the last 3 months (as of May 2026)
