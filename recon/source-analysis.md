# Client-Side Source Analysis

**Target:** https://worldviewosint.com
**Date:** 2026-05-21

---

## Page Structure

### HTML Document (20,848 bytes)
- `<!DOCTYPE html>` with `<html lang="es">`
- Single-page application — entire UI in one HTML file
- Vue 3 `v-cloak` directive on `#app` div
- All CSS is inline in `<style>` block (no external stylesheets except fonts + Mapbox)
- All Vue templates are inline in HTML (not compiled components)

### JavaScript Files
| File | Size | Source | Purpose |
|------|------|--------|---------|
| `mapbox-gl.js` v3.1.2 | ~800KB | api.mapbox.com | Map rendering engine |
| `vue.global.prod.js` v3 | ~135KB | unpkg.com | UI framework |
| `axios.min.js` | ~13KB | cdn.jsdelivr.net | HTTP client |
| **`app.js`** | **12,410 bytes** | Same origin | **Application logic (CRITICAL)** |
| CF challenge script | ~5KB | /cdn-cgi/ | Cloudflare bot management |

### External Domains Referenced
1. `fonts.googleapis.com` — Google Fonts (JetBrains Mono, Orbitron)
2. `fonts.gstatic.com` — Font files
3. `api.mapbox.com` — Mapbox GL JS + CSS + tiles
4. `unpkg.com` — Vue.js CDN
5. `cdn.jsdelivr.net` — Axios CDN
6. `a.nel.cloudflare.com` — Cloudflare NEL reporting

---

## app.js Analysis (FULL SOURCE CAPTURED)

### File: `captures/app.js` — 178 lines, 12,410 bytes

**No obfuscation.** The entire application logic is readable, unminified JavaScript.

### API Base URL
```javascript
var API = '';  // Empty string = same origin
var api = axios.create({baseURL: API, timeout: 15000, withCredentials: true});
```

### Mapbox Token
```javascript
mapboxgl.accessToken = '[REDACTED — Mapbox public token for account juanes2794]';
```
- **Account:** `juanes2794`
- **Status:** EXPOSED — public token in client-side code

### Telegram References
- **Line 87 (HTML):** `<button class="btn" @click="sendReport">TG REPORT</button>`
- **Line 165 (app.js):** `sendReport: function(){ api.get('/api/telegram/report')... }`
- **No direct calls to api.telegram.org**
- **No bot token in client-side code**
- **No chat_id in client-side code**

### API Endpoints Called
```
GET /api/risk-summary
GET /api/osint/conflicts
GET /api/osint/thermal
GET /api/osint/oryx
GET /api/osint/maritime
GET /api/osint/security
GET /api/osint/disasters
GET /api/osint/aviation
GET /api/portfolio
GET /api/osint/losses
GET /api/osint/economic
GET /api/osint/infra
GET /api/ai/status
GET /api/ai/force
GET /api/telegram/report
POST /api/ai/toggle  (body: {enabled: bool})
```

### Hardcoded Secrets Search
| Pattern | Found? | Detail |
|---------|:------:|--------|
| API key | **YES** | Mapbox token (public key, not secret key) |
| Telegram bot token | No | Server-side only |
| Firebase/Supabase | No | Not used |
| Google Analytics | No | Not used |
| Other analytics | No | No tracking code |
| Hardcoded passwords | No | None |
| Environment variables | No | No `.env` references |

### Browser Fingerprinting
| Technique | Present? |
|-----------|:--------:|
| Canvas fingerprinting | No |
| WebGL fingerprinting | No |
| AudioContext fingerprinting | No |
| Font enumeration | No |
| Navigator property collection | No |

### Client-Side Storage
- No `localStorage` usage in app.js
- No `sessionStorage` usage in app.js
- No `IndexedDB` usage in app.js
- No cookie manipulation in app.js
- Axios has `withCredentials: true` (will send cookies if server sets them)

### Service Workers
- No service worker registration in app.js
- `/sw.js` returns SPA HTML (not a real service worker)
- `/service-worker.js` returns SPA HTML

### Source Maps
- No `.map` files exist for any JavaScript
- `app.js` is unobfuscated and readable — source maps are unnecessary

---

## Cloudflare Challenge Script Analysis

Hidden iframe injection at the end of `<body>`:
```javascript
(function(){
  function c(){
    var b = a.contentDocument || a.contentWindow.document;
    if(b){
      var d = b.createElement('script');
      d.innerHTML = "window.__CF$cv$params={r:'9ff38568ac25b6c2',t:'MTc3OTM2NTg3OQ=='};...";
      // Loads /cdn-cgi/challenge-platform/scripts/jsd/main.js
    }
  }
  var a = document.createElement('iframe');
  a.height = 1; a.width = 1;
  a.style.position = 'absolute';
  a.style.visibility = 'hidden';
  document.body.appendChild(a);
})();
```

- Creates a 1x1 hidden iframe
- Loads Cloudflare's JavaScript challenge platform
- Decoding `MTc3OTM2NTg3OQ==` (base64) = `1779365879` (Unix timestamp)
- This is standard Cloudflare Bot Management — NOT custom tracking

---

## CSS Analysis

All CSS is inline (77 lines minified). Key observations:
- **Color scheme:** Dark theme (background: #020617)
- **Primary color:** Cyan (#06b6d4) for UI accents
- **Fonts:** JetBrains Mono (monospace) + Orbitron (headings)
- **Responsive:** Media query at 900px hides sidebar on mobile
- **Scanline effect:** Full-screen overlay simulating CRT monitor scanlines
- **Mapbox popup** styles customized to match dark theme
- **No external CSS frameworks** (no Tailwind, no Bootstrap)

---

## Summary

The entire client-side application is transparent and readable. There is no obfuscation, no hidden tracking, no fingerprinting beyond Cloudflare's standard bot management. The only credential exposed is the Mapbox public token. All sensitive operations (Telegram, AI API calls, data aggregation) are handled server-side.
