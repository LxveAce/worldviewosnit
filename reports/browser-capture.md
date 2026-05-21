# Browser Capture Analysis — worldviewosint.com

**Date:** 2026-05-21
**Tool:** Playwright (Chromium headless, 1920x1080)
**Duration:** ~80 seconds (10s initial load + 50s polling cycle + tab interaction)

---

## Summary

| Metric | Value |
|--------|-------|
| Total network requests | 98 |
| API requests | 42 |
| Mapbox tile/asset requests | 38 |
| WebSocket frames | 0 |
| Console messages | 4 (all WebGL warnings) |
| Cookies | 1 |
| localStorage keys | 2 |
| sessionStorage keys | 0 |

---

## Storage Analysis

### localStorage

| Key | Value | Significance |
|-----|-------|--------------|
| `mapbox.eventData.uuid:anVhbmVzMjc5NA==` | `null` | Base64 = `juanes2794` — confirms Mapbox account ownership |
| `mapbox.eventData:anVhbmVzMjc5NA==` | `{"lastSuccess":1779384012041,"tokenU":"juanes2794"}` | Mapbox telemetry data, explicit username |

**Finding:** The base64 value `anVhbmVzMjc5NA==` decodes to `juanes2794`, confirming the Mapbox account holder. The `tokenU` field in the event data also explicitly names the user.

### Cookies

| Name | Domain | Secure | HttpOnly | SameSite |
|------|--------|--------|----------|----------|
| `cf_clearance` | `.worldviewosint.com` | Yes | Yes | None |

Single cookie — Cloudflare bot-verification clearance token. No application-level session cookies, which confirms the app has no user session management client-side.

### sessionStorage

Empty — no session-scoped data stored.

---

## Vue.js App State

**Result:** `hasVueApp: false`

The Vue 3 instance was not detectable via standard `__vue_app__` property inspection. This is expected for CDN-loaded Vue apps (loaded via `<script>` tag from `unpkg.com`) as opposed to build-tool compiled apps. The app initializes Vue without the dev tools hook.

---

## Polling Behavior (Confirmed)

Three full polling cycles captured in 80 seconds:

| Cycle | Timestamp | Endpoints Hit |
|-------|-----------|---------------|
| 1 (initial) | 17:20:13 | 13 endpoints (all GET) |
| 2 | 17:20:54 | 13 endpoints (~41s after initial) |
| 3 | 17:21:39 | 13 endpoints (~45s after cycle 2) |

**Aviation polled separately** at higher frequency:
- 17:20:39 (26s after initial — separate from full cycle)
- 17:21:09 (30s later)
- 17:21:40 (31s later, coincides with cycle 3)

### Endpoints per polling cycle (13 total):

1. `/api/risk-summary`
2. `/api/osint/conflicts`
3. `/api/osint/thermal`
4. `/api/osint/oryx`
5. `/api/osint/maritime`
6. `/api/osint/security`
7. `/api/osint/disasters`
8. `/api/osint/aviation`
9. `/api/portfolio`
10. `/api/osint/losses`
11. `/api/osint/economic`
12. `/api/osint/infra`
13. `/api/ai/status`

All returned HTTP 200. No authentication sent. Aviation gets an additional dedicated poll at ~30s intervals.

---

## Network Request Breakdown

| Type | Count | Details |
|------|-------|---------|
| document | 1 | Initial HTML page load |
| stylesheet | 2 | Mapbox GL CSS + app styles |
| script | 10 | Vue, Mapbox GL JS, Chart.js, app.js, etc. |
| font | 5 | Web fonts |
| fetch | 36 | API polling (modern fetch API) |
| xhr | 44 | Mapbox tile loading (XMLHttpRequest) |

### Mapbox Requests (38 total)

- `mapbox-gl.css` + `mapbox-gl.js` (v3.1.2)
- Style: `mapbox/dark-v11`
- Tilesets: `mapbox-streets-v8`, `mapbox-terrain-v2`, `mapbox-bathymetry-v2`
- Sprite sheets for map icons
- Multiple vector tile requests for the globe view
- All access tokens redacted in capture

---

## Console Output

4 messages total — all WebGL performance warnings from Mapbox GL:

```
[.WebGL-0x154400192000]GL Driver Message (OpenGL, Performance, GL_CLOSE_PATH_NV, High): GPU stall due to ReadPixels
```

No JavaScript errors, no application-level console messages. The app's built-in console logging system (`consoleLogs`) is internal to the Vue instance and not exposed to the browser console.

---

## WebSocket Analysis

**Zero WebSocket connections detected.**

This definitively confirms the app uses HTTP polling exclusively. No Socket.IO, no raw WebSocket, no Server-Sent Events. All real-time data updates happen through periodic GET requests at 30-45 second intervals.

---

## Screenshots Captured

| File | Description |
|------|-------------|
| `initial_load.png` | Globe view with conflict hotspots on initial load |
| `after_10s.png` | After first data polling cycle completes |
| `tab_intel.png` | INTEL tab — default intelligence view |
| `tab_losses.png` | LOSSES tab — equipment loss tracking with red progress bars |
| `tab_econ.png` | ECON tab — economic indicators and charts |
| `tab_ai.png` | AI tab — AI analysis panel |
| `after_polling.png` | Final state after full 50s polling cycle |

---

## Security-Relevant Findings

1. **No application cookies** — Only Cloudflare `cf_clearance`. App has no session management.
2. **No authentication on polling** — All 13 API endpoints polled without any auth tokens or headers.
3. **Mapbox token in localStorage** — Base64-encoded username stored as localStorage key.
4. **No CSP violations** — All resources loaded successfully (CDN-loaded from unpkg, cdnjs, mapbox).
5. **No WebSocket = no persistent connection** — All data is fetched, never pushed.
6. **fetch + xhr split** — App uses modern `fetch()` for API calls, Mapbox uses `XMLHttpRequest` for tiles.
