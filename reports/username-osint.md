# Username OSINT — juanes2794

**Date:** 2026-05-21
**Tools:** Custom 45-platform scanner (`scripts/username_osint.py`) + Maigret (failed — 91% connection errors)

---

## Summary

**10 accounts found** across 45 platforms tested. Username `juanes2794` originates from Mapbox localStorage data (base64 `anVhbmVzMjc5NA==`).

---

## Accounts Found

| Platform | URL | Category | Confidence |
|----------|-----|----------|------------|
| Reddit | https://www.reddit.com/user/juanes2794 | Social | HIGH — 200 response, profile exists |
| Twitch | https://www.twitch.tv/juanes2794 | Streaming | HIGH — 200 response |
| PyPI | https://pypi.org/user/juanes2794/ | Dev/Packages | HIGH — 200 response, check for published packages |
| Kaggle | https://www.kaggle.com/juanes2794 | Data Science | HIGH — 200 response |
| Steam | https://steamcommunity.com/id/juanes2794 | Gaming | HIGH — 200 response |
| Signal | https://signal.me/#juanes2794 | Messaging | LOW — URL format doesn't confirm account existence |
| Discord | https://discord.com/users/juanes2794 | Messaging | LOW — URL format doesn't confirm account existence |
| Threads | https://www.threads.net/@juanes2794 | Social | MEDIUM — 200 response, may be soft-200 |
| TryHackMe | https://tryhackme.com/p/juanes2794 | Cybersecurity | HIGH — 200 response, profile exists |
| HackTheBox | https://app.hackthebox.com/users/juanes2794 | Cybersecurity | MEDIUM — may redirect to login |

---

## Not Found (24 platforms)

Twitter/X, Instagram, TikTok, YouTube, Pinterest, Medium, Dev.to, Keybase, Gravatar, About.me, Linktree, DockerHub, RubyGems, Replit, CodePen, GitLab, Bitbucket, SourceForge, npm, Patreon, Behance, Dribbble, Flickr, Vimeo, SoundCloud, Spotify, Xbox, Telegram, Mastodon, Facebook, LinkedIn, Crunchbase, HackerOne, BugCrowd

---

## Errors (11 platforms)

Mostly connection timeouts or blocks (Hackernews rate-limited, others timed out).

---

## Analysis

### Developer Profile

The combination of **TryHackMe + HackTheBox + Kaggle + PyPI** paints a clear picture:
- Active in **cybersecurity** (both learning platforms present)
- **Data science / ML** background (Kaggle)
- **Python developer** (PyPI — may have published packages)
- Likely building worldviewosint.com as a personal project combining OSINT + data visualization skills

### Verification Priority

| Priority | Platform | Why |
|----------|----------|-----|
| 1 | **PyPI** | May have published Python packages revealing code style, other projects |
| 2 | **Reddit** | Post/comment history may reveal interests, expertise, other projects |
| 3 | **TryHackMe** | Public profile shows completed rooms, badges, security knowledge level |
| 4 | **Kaggle** | Notebooks/datasets may reveal data processing techniques used in worldviewosint |
| 5 | **Steam** | Low intel value but confirms "juanes" as a personal identity, not a throwaway |

### Notable Absences

- **GitHub**: Not found — unusual for a developer. Possible explanations:
  - Uses a different username on GitHub
  - Private repositories only
  - Self-hosts git (the server runs from a Docker build, no public repo reference)
- **LinkedIn**: Not found — harder to confirm (LinkedIn blocks scrapers aggressively)
- **npm**: Not found — despite Node.js backend, doesn't publish packages publicly

### Geographic Correlation

WHOIS data showed registrant in Valle del Cauca, Colombia. "Juanes" is a common Colombian name (cf. the musician). The combination of:
- Spanish-origin username
- Colombian registration
- Cybersecurity platform presence
- OSINT-focused dashboard project

suggests a Colombian cybersecurity enthusiast/professional building intelligence tools.

---

## Maigret Results

Maigret (3,158 site database) was attempted but returned **0 accounts** due to 91% connection failure rate. The tool makes too many parallel connections from a single IP, triggering rate limiting across platforms. Our custom sequential scanner with 0.5s delays performed significantly better.

---

## Raw Data

- Custom scanner results: `logs/username_osint.json`
- Maigret results: `logs/maigret_results/report_juanes2794_ndjson.json`
