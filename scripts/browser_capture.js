const { chromium } = require('playwright');
const fs = require('fs');
const path = require('path');

const TARGET = 'https://worldviewosint.com';
const OUTDIR = path.join(__dirname, '..', 'captures', 'browser');

async function run() {
    fs.mkdirSync(OUTDIR, { recursive: true });

    const browser = await chromium.launch({ headless: true });
    const context = await browser.newContext({
        viewport: { width: 1920, height: 1080 },
        userAgent: 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    });

    const page = await context.newPage();

    const networkLog = [];
    const consoleLog = [];
    const wsFrames = [];

    // Capture all network requests
    page.on('request', req => {
        networkLog.push({
            timestamp: new Date().toISOString(),
            method: req.method(),
            url: req.url(),
            type: req.resourceType(),
            headers: req.headers(),
        });
    });

    page.on('response', async resp => {
        const req = networkLog.find(r => r.url === resp.url() && !r.status);
        if (req) {
            req.status = resp.status();
            req.responseHeaders = resp.headers();
            req.contentType = resp.headers()['content-type'] || '';
            // Capture API response bodies
            if (resp.url().includes('/api/') && resp.status() === 200) {
                try {
                    const body = await resp.text();
                    req.body = body.substring(0, 5000);
                } catch {}
            }
        }
    });

    // Capture WebSocket connections
    page.on('websocket', ws => {
        console.log(`[WS] WebSocket opened: ${ws.url()}`);
        wsFrames.push({ type: 'open', url: ws.url(), timestamp: new Date().toISOString() });

        ws.on('framesent', frame => {
            wsFrames.push({ type: 'sent', data: frame.payload?.toString()?.substring(0, 500), timestamp: new Date().toISOString() });
        });

        ws.on('framereceived', frame => {
            wsFrames.push({ type: 'received', data: frame.payload?.toString()?.substring(0, 500), timestamp: new Date().toISOString() });
        });

        ws.on('close', () => {
            wsFrames.push({ type: 'close', url: ws.url(), timestamp: new Date().toISOString() });
        });
    });

    // Capture console output
    page.on('console', msg => {
        consoleLog.push({
            type: msg.type(),
            text: msg.text(),
            timestamp: new Date().toISOString(),
        });
    });

    // Capture JavaScript errors
    page.on('pageerror', error => {
        consoleLog.push({
            type: 'error',
            text: error.message,
            timestamp: new Date().toISOString(),
        });
    });

    console.log('[*] Navigating to target...');
    await page.goto(TARGET, { waitUntil: 'networkidle', timeout: 60000 });

    console.log('[*] Page loaded, taking initial screenshot...');
    await page.screenshot({ path: path.join(OUTDIR, 'initial_load.png'), fullPage: true });

    // Wait for Vue app to initialize and first data load
    console.log('[*] Waiting 10s for initial data polling...');
    await page.waitForTimeout(10000);
    await page.screenshot({ path: path.join(OUTDIR, 'after_10s.png'), fullPage: true });

    // Capture localStorage and sessionStorage
    const storage = await page.evaluate(() => {
        const ls = {};
        const ss = {};
        for (let i = 0; i < localStorage.length; i++) {
            const key = localStorage.key(i);
            ls[key] = localStorage.getItem(key);
        }
        for (let i = 0; i < sessionStorage.length; i++) {
            const key = sessionStorage.key(i);
            ss[key] = sessionStorage.getItem(key);
        }
        return { localStorage: ls, sessionStorage: ss };
    });
    console.log(`[*] LocalStorage: ${Object.keys(storage.localStorage).length} keys`);
    console.log(`[*] SessionStorage: ${Object.keys(storage.sessionStorage).length} keys`);

    // Capture cookies
    const cookies = await context.cookies();
    console.log(`[*] Cookies: ${cookies.length}`);

    // Capture Vue app state if accessible
    const appState = await page.evaluate(() => {
        try {
            const app = document.querySelector('#app');
            if (app && app.__vue_app__) {
                const state = app.__vue_app__._instance?.proxy;
                if (state) {
                    return {
                        hasVueApp: true,
                        dataKeys: Object.keys(state.$data || {}),
                    };
                }
            }
            // Try Vue 2 style
            if (app && app.__vue__) {
                return {
                    hasVueApp: true,
                    dataKeys: Object.keys(app.__vue__.$data || {}),
                };
            }
            return { hasVueApp: false };
        } catch (e) {
            return { error: e.message };
        }
    });
    console.log(`[*] Vue app state: ${JSON.stringify(appState)}`);

    // Try to interact with the UI - click through tabs
    console.log('[*] Interacting with UI...');
    const tabs = ['INTEL', 'LOSSES', 'ECON', 'AI'];
    for (const tab of tabs) {
        try {
            await page.click(`text="${tab}"`, { timeout: 3000 });
            await page.waitForTimeout(2000);
            const tabName = tab.toLowerCase();
            await page.screenshot({ path: path.join(OUTDIR, `tab_${tabName}.png`) });
            console.log(`[*] Clicked tab: ${tab}`);
        } catch {
            console.log(`[*] Tab not found: ${tab}`);
        }
    }

    // Wait through one full polling cycle (45s)
    console.log('[*] Waiting 50s for full polling cycle...');
    await page.waitForTimeout(50000);
    await page.screenshot({ path: path.join(OUTDIR, 'after_polling.png'), fullPage: true });

    // Capture the console panel content
    const consolePanelContent = await page.evaluate(() => {
        const panel = document.querySelector('.console-panel') ||
                      document.querySelector('[class*="console"]') ||
                      document.querySelector('.logs');
        return panel ? panel.innerText : 'Console panel not found';
    });

    // Count network requests by type
    const requestsByType = {};
    const apiRequests = [];
    for (const req of networkLog) {
        requestsByType[req.type] = (requestsByType[req.type] || 0) + 1;
        if (req.url.includes('/api/')) {
            apiRequests.push({
                method: req.method,
                url: req.url,
                status: req.status,
                timestamp: req.timestamp,
            });
        }
    }

    // Capture Mapbox tile requests
    const mapboxRequests = networkLog.filter(r => r.url.includes('mapbox'));
    console.log(`[*] Mapbox requests: ${mapboxRequests.length}`);

    // Final summary
    console.log('\n=== CAPTURE SUMMARY ===');
    console.log(`Total network requests: ${networkLog.length}`);
    console.log(`API requests: ${apiRequests.length}`);
    console.log(`WebSocket frames: ${wsFrames.length}`);
    console.log(`Console messages: ${consoleLog.length}`);
    console.log(`Cookies: ${cookies.length}`);
    console.log(`Request types: ${JSON.stringify(requestsByType)}`);

    // Save all data
    const results = {
        timestamp: new Date().toISOString(),
        target: TARGET,
        summary: {
            total_requests: networkLog.length,
            api_requests: apiRequests.length,
            websocket_frames: wsFrames.length,
            console_messages: consoleLog.length,
            cookies: cookies.length,
            mapbox_requests: mapboxRequests.length,
            request_types: requestsByType,
        },
        storage,
        cookies,
        app_state: appState,
        console_panel: consolePanelContent,
        api_requests: apiRequests,
        websocket_frames: wsFrames,
        console_log: consoleLog,
        mapbox_requests: mapboxRequests.map(r => ({
            url: r.url.replace(/access_token=[^&]+/, 'access_token=[REDACTED]'),
            type: r.type,
            status: r.status,
        })),
        network_log: networkLog.map(r => ({
            method: r.method,
            url: r.url.replace(/access_token=[^&]+/, 'access_token=[REDACTED]'),
            type: r.type,
            status: r.status,
            timestamp: r.timestamp,
        })),
    };

    fs.writeFileSync(
        path.join(OUTDIR, 'browser_capture.json'),
        JSON.stringify(results, null, 2)
    );

    console.log(`\nSaved to captures/browser/`);

    await browser.close();
}

run().catch(e => {
    console.error('Error:', e.message);
    process.exit(1);
});
