# 🧠 Ultimate Web Intelligence & Reverse Engineering Lab

## 🎯 Mission

Perform a full-spectrum technical, behavioral, and security analysis of:

https://worldviewosint.com/

You will behave as an autonomous:

- OSINT analyst  
- network traffic analyst  
- reverse engineer  
- backend inference engine  

Your goal is to **capture, analyze, reconstruct, and classify** everything observable from the client side.

---

# ⚠️ Operating Principles

- Operate autonomously
- Log ALL observable data
- Do NOT attempt exploitation or unauthorized access
- Focus on observation, inference, reconstruction
- Prefer evidence over assumptions
- Remain low-noise during probing

---

# 🧰 TOOLCHAIN SETUP

Install automatically:

## Core:
- Node.js (latest LTS)
- Python 3.11+
- jq
- curl / httpie

## Browser:
- Playwright
- Chromium

## Network Interception:
- mitmproxy

## Optional:
- tcpdump / Wireshark

---

# 🌐 ARCHITECTURE STACK
[Agent]
↓
[Playwright Automation]
↓
[Chromium Browser]
↓
[mitmproxy Interception Layer]
↓
[Target Site + APIs + Telegram Endpoints]


---

# 🧪 PHASE 1 — NETWORK INTERCEPTION SETUP

1. Start mitmproxy:mitmproxy -w traffic_dump.mitm
2. Configure browser proxy:127.0.0.1:8080


3. Install certificate:
Visit:http://mitm.it

Trust certificate to enable HTTPS decryption.

---

# 🧪 PHASE 2 — FULL TRAFFIC CAPTURE

Launch Chromium via Playwright with proxy enabled.

Capture ALL:

- XHR / fetch requests  
- WebSockets  
- scripts  
- images  
- third-party APIs  

Log for each:

- URL  
- method  
- headers  
- request body  
- response body  
- timestamp  

Store:

- JSON logs  
- HAR file  

---

# 🧪 PHASE 3 — BEHAVIOR SIMULATION

Simulate real usage:

- initial load  
- wait for background polling (~15–20s)  
- interact with UI:
  - clicks
  - toggles
  - refreshes  

Trigger additional network activity.

---

# 🧪 PHASE 4 — DATA LOGGING

Create structured outputs:

- unique endpoints list  
- grouped responses by endpoint  
- frequency tracking  
- payload size tracking  

---

# 🧪 PHASE 5 — TELEGRAM FORENSICS (CRITICAL)

Detect traffic to:


api.telegram.org

For EACH request:

Extract:

- full URL  
- endpoint type (sendMessage, etc.)  
- request payload  
- response  

Decode:

- chat_id  
- text content  

Determine:

- trigger condition (load, click, polling)  
- frequency  
- data included:
  - IP
  - user agent
  - interaction data  

Classify:

- logging system  
- alert system  
- tracking behavior  

---

# 🧪 PHASE 6 — ENDPOINT DISCOVERY

From observed endpoints:

Generate:

- /api/*
- /internal/*
- /debug/*
- /v1/*
- /admin/*

Make safe requests:

- log status codes  
- log response sizes  

Classify:

- valid  
- hidden  
- dead  

---

# 🧪 PHASE 7 — DATA SOURCE CLASSIFICATION

For ALL data streams:

Label as:

- STATIC (hardcoded)  
- REAL-TIME API  
- AGGREGATED (RSS)  
- SYNTHETIC  

---

# 🧪 PHASE 8 — BACKEND FINGERPRINTING

Extract headers:

- server  
- x-powered-by  
- x-vercel-id  

Infer:

| Signal | Meaning |
|--------|--------|
| Next.js | React frontend |
| uvicorn | Python backend |
| nginx | generic server |
| x-vercel-id | Vercel hosting |

Determine:

- serverless vs traditional  
- caching behavior  
- polling frequency  

---

# 🧪 PHASE 9 — API REPLAY

Replay endpoints using:


curl
httpie

Compare:

- browser response vs replay response  

Detect:

- auth requirements  
- static vs dynamic  
- rate limits  

---

# 🧪 PHASE 10 — SIGNAL VALIDATION

Analyze dataset quality:

Detect:

- repeated entries  
- identical refresh cycles  
- unrealistic severity values  
- inconsistent timestamps  

Assign confidence:

- HIGH (real)  
- MED (transformed)  
- LOW (synthetic)  

---

# 🧪 PHASE 11 — BEHAVIOR MODELING

Reconstruct system logic:

### Data lifecycle:
- ingestion
- transformation
- display

### UI → network relationships:
- what triggers calls

### Purpose classification:
- visualization  
- monitoring  
- tracking  

Produce flow diagram.

---

# 🧪 PHASE 12 — SECURITY ANALYSIS

Evaluate:

## Data Exfiltration:
- outbound communication (Telegram etc.)

## Tracking:
- IP logging  
- session patterns  
- fingerprinting  

## Risk Classification:

- LOW  
- MEDIUM  
- HIGH  

Provide justification.

---

# 🧬 PHASE 13 — ADVANCED CORRELATION

Cross-analyze:

- repeated payloads  
- shared structures  
- timing intervals  

Detect:

- fake “live” updates  
- cached feeds  
- synthetic behavior loops  

---

# 🧬 PHASE 14 — SYSTEM INTENT INFERENCE

Determine what this system really is:

- UI demo  
- OSINT visualization  
- monitoring dashboard  
- tracking/logging tool  

---

# 📊 OUTPUT REQUIREMENTS

Produce structured report:

## 1. Architecture Diagram
(text-based)

## 2. API Map
(all endpoints)

## 3. Telegram Analysis
- endpoints
- payloads
- purpose

## 4. Data Authenticity Report

## 5. Backend Fingerprint

## 6. Security Risk Assessment

## 7. Final Classification:
- demo / prototype / operational system

---

# 🧠 AUTOMATION SCRIPT (Playwright + Proxy)

```javascript
const { chromium } = require('playwright');
const fs = require('fs');

(async () => {
  const browser = await chromium.launch({
    headless: false,
    proxy: { server: "http://127.0.0.1:8080" }
  });

  const context = await browser.newContext({
    recordHar: { path: 'traffic.har' }
  });

  const page = await context.newPage();
  const logs = [];

  page.on('request', req => {
    logs.push({
      type: "request",
      time: Date.now(),
      url: req.url(),
      method: req.method(),
      headers: req.headers(),
      body: req.postData()
    });
  });

  page.on('response', async res => {
    let body = null;
    try { body = await res.text(); } catch {}

    logs.push({
      type: "response",
      time: Date.now(),
      url: res.url(),
      status: res.status(),
      headers: res.headers(),
      body: body
    });
  });

  await page.goto('https://worldviewosint.com/');
  await page.waitForTimeout(20000);

  await page.mouse.click(300, 300);
  await page.waitForTimeout(5000);

  fs.writeFileSync("network.json", JSON.stringify(logs, null, 2));

  await browser.close();
})();
