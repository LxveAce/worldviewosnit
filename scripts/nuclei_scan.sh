#!/bin/bash
# Nuclei vulnerability scan for worldviewosint.com
# Requires: nuclei installed via go install

export PATH="$HOME/go/bin:$PATH"

TARGET="https://worldviewosint.com"
OUTDIR="$(dirname "$0")/../logs"

echo "=== NUCLEI VULNERABILITY SCAN ==="
echo "Target: $TARGET"
echo ""

# Update templates first
echo "[*] Updating nuclei templates..."
nuclei -update-templates 2>&1 | tail -5

echo ""
echo "[*] Running scan..."

# Run nuclei with multiple template categories
nuclei -u "$TARGET" \
    -t cves/ \
    -t exposures/ \
    -t misconfiguration/ \
    -t technologies/ \
    -t default-logins/ \
    -t vulnerabilities/ \
    -t file/ \
    -severity critical,high,medium,low \
    -stats \
    -json-export "$OUTDIR/nuclei_scan.json" \
    -o "$OUTDIR/nuclei_scan.txt" \
    -rate-limit 10 \
    -bulk-size 5 \
    -concurrency 3 \
    2>&1

echo ""
echo "[*] Scan complete."
echo "Results: $OUTDIR/nuclei_scan.txt"
echo "JSON: $OUTDIR/nuclei_scan.json"

# Also scan specific API endpoints
echo ""
echo "[*] Scanning API endpoints..."
cat <<'URLS' > /tmp/worldview_urls.txt
https://worldviewosint.com/api/health
https://worldviewosint.com/api/risk-summary
https://worldviewosint.com/api/osint/conflicts
https://worldviewosint.com/api/osint/thermal
https://worldviewosint.com/api/osint/oryx
https://worldviewosint.com/api/osint/maritime
https://worldviewosint.com/api/osint/security
https://worldviewosint.com/api/osint/disasters
https://worldviewosint.com/api/osint/aviation
https://worldviewosint.com/api/portfolio
https://worldviewosint.com/api/osint/losses
https://worldviewosint.com/api/osint/economic
https://worldviewosint.com/api/osint/infra
https://worldviewosint.com/api/ai/status
https://worldviewosint.com/api/ai/toggle
https://worldviewosint.com/api/ai/force
https://worldviewosint.com/api/ai/analyze
https://worldviewosint.com/api/telegram/report
https://worldviewosint.com/docker-compose.yml
URLS

nuclei -l /tmp/worldview_urls.txt \
    -t cves/ \
    -t exposures/ \
    -t misconfiguration/ \
    -t technologies/ \
    -severity critical,high,medium,low \
    -stats \
    -json-export "$OUTDIR/nuclei_api_scan.json" \
    -o "$OUTDIR/nuclei_api_scan.txt" \
    -rate-limit 10 \
    2>&1

echo ""
echo "=== SCAN COMPLETE ==="
