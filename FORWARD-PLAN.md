# LxveAce/worldviewosnit - Forward Plan

> Status: Mature PUBLIC OSINT recon dossier on third-party worldviewosint.com - evidence archive complete & valid, but scripts are unrunnable on this clone and the git email leaks PII. Health: YELLOW. Date: <YYYY-MM-DD>.

## Where this stands

**What it is.** `worldviewosnit` is NOT a buildable/deployable application. It is a structured OSINT + security-reconnaissance dossier targeting the third-party website `https://worldviewosint.com`. The repo is an evidence archive: ~22 standalone Python recon scripts (mostly stdlib urllib/ssl/socket) + one Playwright Node.js capture script (`scripts/browser_capture.js`), captured artifacts (`captures/`), raw logs (`logs/`), recon notes (`recon/`), and 13 generated analysis reports (`reports/`), plus `README.md` (the playbook), `NEXT-STEPS.md`, `wordlist.txt`, `LICENSE` (MIT), `SECURITY.md`.

**How it "runs".** There is no build/CI/release pipeline (no workflows, no tests, 0 releases, 0 tags, no GitHub Pages). 
- Node: `package.json` declares only `playwright ^1.60.0`; run the one JS entry point via `npx playwright` against `scripts/browser_capture.js`. `node_modules/` is gitignored/absent, so it currently leans on a globally installed playwright.
- Python: run scripts individually (`python scripts/<name>.py`). Most use only the stdlib; `scripts/shodan_search.py` needs the PyPI `shodan` package + `SHODAN_API_KEY`. There is **no** `requirements.txt`.

**Current state.** Single branch `main`; HEAD `6a5570e` "Scrub legal name and personal email; attribute to alias". 0 open issues, 0 releases. The evidence archive is functional and valid (all sampled captures/logs parse as JSON; `browser_capture.js` passes `node --check`; all Python scripts pass `py_compile`). The analysis verdict (`reports/final-classification.md`, HIGH confidence) classifies the TARGET as an operational solo-developer OSINT dashboard (Vue 3 CDN + Mapbox + Node, dated 2026-05-21). The repo is near-complete (NEXT-STEPS.md: 15/15 core items, all tiers executed) - build on existing artifacts, do not redo recon from scratch.

**The catch.** The executable scripts are NOT runnable on this clone: 22 Python files hardcode `C:\Users\mmrla\worldviewosnit\...` while the real clone is `C:\Users\mmrla\repos\worldviewosnit` (the `repos` segment is missing), so reads/writes crash. And the local git `user.email` is the personal gmail, which would leak PII on the next commit.

## P0 - do first

1. **Fix the git author email before ANY new commit.** Verified: `user.email=lxveace@proton.me`, `user.name=LxveAce`, last commit author = correct noreply alias. The next commit would leak personal PII into public commit metadata, violating the standing LxveAce public-repo rule. Run: `git config user.email 251227901+LxveAce@users.noreply.github.com` (in this clone only).
2. **Fix the hardcoded absolute path in 22 Python scripts.** They reference `C:\Users\mmrla\worldviewosnit\...` (missing `repos`), so every read/write crashes with `FileNotFoundError`. Replace with `__file__`-relative paths, e.g. `os.path.join(os.path.dirname(__file__), '..', 'logs', '<name>.json')`, so scripts run on any clone.
3. **Make the public-disclosure decision.** This repo documents a third party's live vulnerabilities with reproducible steps and names the developer. Confirm continuing-public with responsible-hardening framing, OR choose private / redaction / responsible-disclosure. No explicit decision note exists in continuity docs - this gates how the security content is written below.

> Note: there is no `.exe`/installer concern here - that item applies to the separate `cyber-controller` repo, not `worldviewosnit`. This is a research/evidence repo with no shippable binary.

## Surface bugs found

| Title | Location | Severity | Note |
|---|---|---|---|
| Local git user.email is personal gmail, violates no-PII rule | `git config user.email` in `C:\Users\mmrla\repos\worldviewosnit` | P0 | Verified; fix: `git config user.email 251227901+LxveAce@users.noreply.github.com` |
| 22 Python scripts hardcode wrong absolute path (missing `repos`) | `scripts/*.py` (e.g. `analyze_endpoints.py:3`, `mapbox_enum.py:13`, `alt_recon.py:176`) | P1 | Real clone is `...\repos\worldviewosnit`; crashes with FileNotFoundError; none use `__file__` |
| Undeclared third-party dep `shodan` (no requirements.txt) | `scripts/shodan_search.py:1`; no `requirements.txt` (verified absent) | P2 | ModuleNotFoundError without `pip install shodan`; reads `SHODAN_API_KEY` from env correctly |
| README/NEXT-STEPS reference files & dirs that do not exist | `README.md` PROJECT STRUCTURE + `NEXT-STEPS.md`: `scripts/capture.js`, `tools/setup.sh`, `scripts/replay.sh`, `scripts/analyze.py`, `captures/traffic.har`, `recon/subdomains.txt` | P2 | Verified absent; actual capture script is `scripts/browser_capture.js` |
| package.json missing name/version; lock root incomplete; no local node_modules | `package.json`, `package-lock.json` (lockfileVersion 3) | P3 | Relies on global playwright; add name/version, document `npm install` + `npx playwright install chromium` |

## Features to add

> USER DIRECTIVES: (none provided for this run.)

- **Add `requirements.txt` (or `pyproject`)** listing every third-party Python dep actually imported (`shodan` confirmed) + an env-var reference (`SHODAN_API_KEY`, audit for others), so the dominant language (~70% Python) is installable from a manifest.
- **Reconcile docs with the real tree:** rename `scripts/capture.js` -> `scripts/browser_capture.js` in `README.md`/`NEXT-STEPS.md`, and remove (or create) the listed-but-missing files (`tools/setup.sh`, `replay.sh`, `analyze.py`, `traffic.har`, `subdomains.txt`).
- **Tidy `package.json`:** add `name`/`version`, regenerate `package-lock.json`, document the two-step Playwright install so `browser_capture.js` does not depend on a global playwright.
- **Cross-link to the user's public security playbook** `vibe-coding-website-security`: its taxonomy (CORS reflection, missing API auth, exposed config, secrets-in-client) directly overlaps these findings - present them as live case-study instances rather than re-derived material.
- **Optional:** add a one-line README note on the intended repo-name spelling (`worldviewosnit` transposed vs target `worldviewosint`).

## Red-team / hardening

This is a PUBLIC repo describing a third party's live infrastructure. Frame everything as responsible hardening, not exploitation.

- **Generalize exploit content into case studies.** Convert step-by-step material (auth-bypass vectors, the CORS credential-reflection PoC in `scripts/cors_poc.py`, exposed docker-compose / no-auth Neo4j writeups) into descriptions of the vulnerability class + fix, WITHOUT a copy-paste recipe against the live target.
- **Reconsider third-party PII.** The target developer's real name appears in `NEXT-STEPS.md` and `reports/final-classification.md`. The user de-identifies themselves yet deanonymizes the target - weigh redaction given the user's own strong privacy stance.
- **Responsible disclosure.** If the documented live vulns are real and current, consider notifying the target (SECURITY.md already uses alias contact `lxveace@proton.me`) before/instead of further public detail.
- **Secret sweep before publish.** A targeted grep found no live `pk.` Mapbox tokens; `browser_capture.js` redacts `access_token` (lines 222/228/231); the `andrew` token in `wordlist.txt` is benign and intentionally left. Do a fuller secret/PII sweep of `captures/` and `logs/` before any new publish.
- **Keep hygiene baseline.** `.gitignore` correctly excludes `*.env`/`.env.*`/`config.ini`/`__pycache__` (verified `__pycache__` is gitignored and NOT tracked). Never bake API keys into new requirements/setup docs.

## Dig deeper (next dedicated session)

1. **Per-script runtime audit.** After fixing paths + adding `requirements.txt`, run each script in passive/dry-run mode against recorded captures or a local fixture to surface runtime errors beyond the static path bug - no script was executed end-to-end in recon.
2. **Complete the dep set.** Pip-resolve / import-scan every module to confirm `shodan` is the only undeclared third-party dep before finalizing `requirements.txt`.
3. **Fresh vs. stale analysis.** The target site is UP now (Vue SPA "WORLDVIEW OSINT | C4ISR v3.2") but findings are dated 2026-05-21. Decide fresh live capture vs. re-analysis; re-run `temporal_capture.py` / `browser_capture.js` if refreshing.
4. **Resolve the target's open technical questions** from `reports/final-classification.md` (server-side Telegram behavior, conflict-data provenance, auth mechanism, AIS data source) - the natural research frontier if the project continues analytically.
5. **Full artifact review.** Read every report/log (e.g. `telegram-report.md`, `cors-vulnerability.md`) to confirm summaries and catch residual PII/secrets before publishing changes.
6. **Release posture.** Currently 0 releases / 0 tags / no Pages. Decide whether anything is meant to be distributed (cut a tagged release) or document git-clone-of-main as the only intended path (fine for a research repo).

## Dependencies & cross-repo context

- **Node:** `package.json` -> only `playwright ^1.60.0`; `scripts/browser_capture.js` is the sole JS entry point (passes `node --check`). No local `node_modules` (gitignored); leans on global playwright today.
- **Python:** ~70% of repo, ~22 scripts. Mostly stdlib; `scripts/shodan_search.py` needs PyPI `shodan` + `SHODAN_API_KEY`. No `requirements.txt` (verified).
- **Infra:** no CI/CD, no Actions, no tests, no releases/tags, no Pages. Single `main`, MIT. Distribution = git clone of `main` HEAD only.
- **Cross-repo:** standalone - NO predecessor/successor or shared-code link with the cyberdeck ecosystem (`cyber-controller`, Projects kit, esp32 firmware). Strong CONTENT overlap (reuse opportunity, not duplicated effort) with the PUBLIC `vibe-coding-website-security` playbook taxonomy.
- **Governance:** LxveAce public-repo rules apply (alias-only commits, NO `Co-Authored-By: Claude`, no PII, alias contact `lxveace@proton.me`). Continuity in `session-context/SESSION.md` and `Projects/CLAUDE-TRANSFER.md`.

## Open questions

- Is the repo INTENDED to remain public given it documents a third party's live vulns and names the developer? No explicit decision note found.
- What is the new flagship task's objective? The repo is near-complete (15/15 core, all tiers) with no defined new scope in continuity docs - the user/orchestrator must set the goal.
- Is the hardcoded-path bug legacy (scripts authored when the clone lived at `...\worldviewosnit` before moving to `...\repos\worldviewosnit`)? Mismatch verified; intent not.
- Are the target findings (uptime, data feeds, developer identity) still accurate? Dated 2026-05-21; site is UP now but specifics unverified.
- Is `shodan` the only undeclared third-party Python dep? Likely, not exhaustively pip-resolved.
- Is the repo-name spelling `worldviewosnit` (transposed) vs target `worldviewosint` intentional?