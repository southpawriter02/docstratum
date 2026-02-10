# v0.4.4b — Docker Infrastructure & Environment Setup

> **Task:** Set up the Docker infrastructure for Neo4j with proper configuration. This document specifies the Docker Compose setup, port mapping strategy, authentication and security considerations, volume management for persistence, environment variables, health checks, and development vs. production configurations.

---

## Objective

Establish a robust Docker infrastructure for Neo4j 5 Community that supports local development, staging, and optional production deployments. This includes a fully-documented Docker Compose configuration, clear port mapping, secure authentication, persistent volume management, health verification, and environment-specific configurations.

---

## Scope Boundaries

| Aspect | In Scope | Out of Scope |
|--------|----------|--------------|
| **Neo4j Versions** | Neo4j 5 Community edition | Neo4j Enterprise, older v4.x versions |
| **Docker Setup** | Docker Compose (single-host) | Kubernetes, Swarm, multi-host orchestration |
| **Ports** | 7474 (HTTP browser), 7687 (Bolt protocol) | Additional custom ports, HTTPS config |
| **Authentication** | Basic auth (neo4j/password123), ENV variables | OAuth, LDAP, SASL, SSO integration |
| **Volumes** | Data persistence, logs, backups | Distributed volume drivers, network mounts |
| **Network** | Host network, bridge network basics | Advanced network policies, service mesh |
| **Health Checks** | Liveness & readiness probes, startup verification | Custom application-specific probes |
| **Configuration** | Configs for dev/staging/test environments | Fine-tuned production memory settings |

---

## Dependency Diagram

```
┌─────────────────────────────────────────────────┐
│   Graph Database Design (v0.4.4a)               │
│  Schema: Concept nodes, DEPENDS_ON edges       │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│   Docker Infrastructure (THIS DOCUMENT)         │
│  Neo4j 5 Community, Docker Compose, Volumes    │
└────────────────┬────────────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────────────┐
│   Graph Population (v0.4.4c)                    │
│  populate_neo4j.py, data import, verification  │
└─────────────────────────────────────────────────┘
```

---

## 1. Docker Compose Configuration

### 1.1 Development Environment (docker-compose.dev.yml)

```yaml
version: '3.9'

services:
  neo4j:
    image: neo4j:5-community
    container_name: docstratum-neo4j-dev

    # Port mappings
    ports:
      - "7474:7474"   # HTTP browser (http://localhost:7474)
      - "7687:7687"   # Bolt protocol (bolt://localhost:7687)

    # Environment configuration
    environment:
      # Authentication
      NEO4J_AUTH: neo4j/password123

      # Java memory allocation (development)
      NEO4J_dbms_memory_heap_initial__size: 512m
      NEO4J_dbms_memory_heap_max__size: 1g
      NEO4J_dbms_memory_pagecache_size: 256m

      # Logging (verbose for development)
      NEO4J_dbms_logs_query_enabled: "true"
      NEO4J_dbms_logs_query_threshold: 0

      # Connection limits (relaxed for dev)
      NEO4J_dbms_connector_bolt_connection__max: 200

      # TLS disabled in dev (security not required)
      NEO4J_dbms_ssl_policy_bolt_enabled: "false"

    # Volume configuration
    volumes:
      # Data persistence
      - neo4j-data-dev:/var/lib/neo4j/data
      # Logs volume
      - neo4j-logs-dev:/var/lib/neo4j/logs
      # Optional: mount local backups directory
      - ./backups:/var/lib/neo4j/backups

    # Health check
    healthcheck:
      test:
        - CMD
        - wget
        - --quiet
        - --tries=1
        - --spider
        - http://localhost:7474
      interval: 5s
      timeout: 3s
      retries: 5
      start_period: 10s

    # Resource limits (permissive for development)
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G

    # Restart policy
    restart: unless-stopped

volumes:
  neo4j-data-dev:
    driver: local
  neo4j-logs-dev:
    driver: local
```

### 1.2 Production Environment (docker-compose.prod.yml)

```yaml
version: '3.9'

services:
  neo4j:
    image: neo4j:5-community
    container_name: docstratum-neo4j-prod

    # Restrict port exposure (use reverse proxy)
    expose:
      - "7687"   # Only expose via reverse proxy

    ports:
      - "7687:7687"   # Bolt only, no HTTP browser in production

    environment:
      # Authentication (strong password required)
      NEO4J_AUTH: neo4j/${NEO4J_PASSWORD}

      # Java memory allocation (production-sized)
      NEO4J_dbms_memory_heap_initial__size: 2g
      NEO4J_dbms_memory_heap_max__size: 4g
      NEO4J_dbms_memory_pagecache_size: 2g

      # Logging (production - minimal logs)
      NEO4J_dbms_logs_query_enabled: "false"
      NEO4J_dbms_logs_gc_enabled: "true"

      # Connection limits (conservative for stability)
      NEO4J_dbms_connector_bolt_connection__max: 100
      NEO4J_dbms_connector_bolt_connection__idle__time__before__connection__timeout: 900000

      # TLS enabled for security
      NEO4J_dbms_ssl_policy_bolt_enabled: "true"
      NEO4J_dbms_ssl_policy_bolt_client__auth: NONE

    volumes:
      # Data persistence with backup strategy
      - neo4j-data-prod:/var/lib/neo4j/data
      - neo4j-logs-prod:/var/lib/neo4j/logs
      # Mount production certificates (if TLS enabled)
      - /etc/docstratum/neo4j/certs:/var/lib/neo4j/certificates
      - /etc/docstratum/neo4j/backups:/var/lib/neo4j/backups

    healthcheck:
      test:
        - CMD
        - cypher-shell
        - -u
        - neo4j
        - -p
        - ${NEO4J_PASSWORD}
        - "RETURN 1"
      interval: 30s
      timeout: 5s
      retries: 3
      start_period: 30s

    # Strict resource limits
    deploy:
      resources:
        limits:
          cpus: '4'
          memory: 8G
        reservations:
          cpus: '2'
          memory: 4G

    # No automatic restart (manual intervention required)
    restart: on-failure:3

    # Logging configuration
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "5"

volumes:
  neo4j-data-prod:
    driver: local
    driver_opts:
      type: nfs
      o: addr=${NFS_SERVER},vers=4,soft,timeo=180,bg,tcp,rw
      device: ":${NFS_PATH}/neo4j-data"
  neo4j-logs-prod:
    driver: local

networks:
  default:
    driver: bridge
    driver_opts:
      com.docker.network.driver.mtu: 1450
```

### 1.3 Test Environment (docker-compose.test.yml)

```yaml
version: '3.9'

services:
  neo4j:
    image: neo4j:5-community
    container_name: docstratum-neo4j-test

    ports:
      - "7474:7474"
      - "7687:7687"

    environment:
      NEO4J_AUTH: neo4j/test_password

      # Minimal memory for testing
      NEO4J_dbms_memory_heap_initial__size: 256m
      NEO4J_dbms_memory_heap_max__size: 512m
      NEO4J_dbms_memory_pagecache_size: 128m

      # Disable query logging for speed
      NEO4J_dbms_logs_query_enabled: "false"

    # Temporary volumes (auto-cleanup)
    volumes:
      - neo4j-data-test:/var/lib/neo4j/data

    healthcheck:
      test: ["CMD", "wget", "--quiet", "--tries=1", "--spider", "http://localhost:7474"]
      interval: 2s
      timeout: 2s
      retries: 10

    deploy:
      resources:
        limits:
          cpus: '1'
          memory: 1G

volumes:
  neo4j-data-test:
    driver: local
```

---

## 2. Port Mapping Strategy

### 2.1 Port Reference Table

| Port | Protocol | Purpose | Default URL | Environment |
|------|----------|---------|-------------|-------------|
| **7474** | HTTP | Neo4j Browser UI | http://localhost:7474 | Dev, Test |
| **7687** | Bolt | Binary protocol (driver connections) | bolt://localhost:7687 | All |
| **7473** | HTTPS | Encrypted HTTP (optional) | https://localhost:7473 | Prod (if enabled) |
| **7688** | TLS | Encrypted Bolt (optional) | bolt+s://localhost:7688 | Prod (if enabled) |

### 2.2 Network Architecture Diagram

```
Development Environment:
┌────────────────────────────────────────────┐
│ Developer Machine (localhost)               │
├────────────────────────────────────────────┤
│  Browser        Python Client              │
│     │                  │                   │
│     ▼                  ▼                   │
│  :7474              :7687                 │
│  (HTTP)            (Bolt)                 │
│     │                  │                   │
│     └──────┬───────────┘                   │
│            ▼                               │
│   ┌──────────────────┐                    │
│   │  Docker Host     │                    │
│   ├──────────────────┤                    │
│   │  [neo4j:5]       │                    │
│   │  - ports 7474    │                    │
│   │  - ports 7687    │                    │
│   │  - volumes       │                    │
│   └──────────────────┘                    │
└────────────────────────────────────────────┘

Production Environment:
┌────────────────────────────────────────────┐
│ Load Balancer / Reverse Proxy               │
│ (nginx/haproxy)                            │
└─────────────┬──────────────────────────────┘
              │
              ▼
┌────────────────────────────────────────────┐
│ Docker Host (Neo4j)                         │
├────────────────────────────────────────────┤
│ :7687 (Bolt, internal only)                │
│ - TLS enabled                              │
│ - Restricted to reverse proxy              │
│ - No HTTP browser exposure                 │
└────────────────────────────────────────────┘
```

### 2.3 Port Binding Configuration

```bash
# Development: Bind to localhost only (secure)
ports:
  - "127.0.0.1:7474:7474"
  - "127.0.0.1:7687:7687"

# Staging: Bind to all interfaces (with firewall protection)
ports:
  - "0.0.0.0:7474:7474"
  - "0.0.0.0:7687:7687"

# Production: Use reverse proxy, no direct exposure
expose:
  - "7687"
# Bolt accessed through reverse proxy only
```

---

## 3. Authentication & Security Considerations

### 3.1 Authentication Strategy

**Development:**
```bash
NEO4J_AUTH=neo4j/password123
# Simple, easy to remember, acceptable for local dev
```

**Production:**
```bash
NEO4J_AUTH=neo4j/${NEO4J_PASSWORD}
# Strong password from secrets manager (Vault, AWS Secrets Manager, etc.)
# Minimum: 12 characters, mixed case, numbers, symbols
```

### 3.2 Password Management Best Practices

```yaml
# .env (development only - DO NOT commit)
NEO4J_PASSWORD=password123
NEO4J_AUTH_REALM=native

# .env.production (secrets management system)
# Use Docker secrets or external vault:
# - AWS Secrets Manager
# - HashiCorp Vault
# - Docker Swarm secrets
# - Kubernetes Secrets

# docker-compose.prod.yml with secrets
services:
  neo4j:
    environment:
      NEO4J_AUTH: neo4j/file:/run/secrets/neo4j_password
    secrets:
      - neo4j_password

secrets:
  neo4j_password:
    external: true
    name: docstratum_neo4j_password
```

### 3.3 Network Security Configuration

```yaml
# Network isolation (production)
networks:
  neo4j-network:
    driver: bridge
    driver_opts:
      # Disable inter-container communication from external networks
      com.docker.network.bridge.enable_icc: "false"

services:
  neo4j:
    networks:
      - neo4j-network
    # No ports exposed to host network directly
    expose:
      - "7687"

  # Only authorized services can access Neo4j
  docstratum-backend:
    networks:
      - neo4j-network
    depends_on:
      neo4j:
        condition: service_healthy
```

### 3.4 TLS/SSL Configuration (Production)

```yaml
environment:
  # Enable TLS for Bolt protocol
  NEO4J_dbms_ssl_policy_bolt_enabled: "true"
  NEO4J_dbms_ssl_policy_bolt_base__directory: /var/lib/neo4j/certificates
  NEO4J_dbms_ssl_policy_bolt_private__key: private.key
  NEO4J_dbms_ssl_policy_bolt_public__certificate: public.crt
  NEO4J_dbms_ssl_policy_bolt_client__auth: NONE

volumes:
  # Mount certificates into container
  - /etc/docstratum/neo4j/certs:/var/lib/neo4j/certificates:ro
```

---

## 4. Volume Management for Data Persistence

### 4.1 Volume Structure

```
neo4j-data/
├── databases/
│   └── neo4j/
│       ├── store/          # Graph store files
│       └── transaction/    # Transaction logs
├── transactions/           # Active transaction logs
└── import/                 # CSV import directory

neo4j-logs/
├── debug.log               # Debug level logs
├── neo4j.log               # Application logs
├── query.log               # Query execution logs (if enabled)
└── gc.log                  # Garbage collection logs
```

### 4.2 Volume Configuration Reference

```yaml
volumes:
  # Development: Local Docker volume
  neo4j-data-dev:
    driver: local
    driver_opts:
      type: tmpfs
      device: tmpfs
      o: size=1g,mode=1777

  # Production: Named volume with backup strategy
  neo4j-data-prod:
    driver: local
    driver_opts:
      type: nfs
      o: addr=backup-server,vers=4,soft,timeo=180,bg,tcp,rw
      device: ":/mnt/neo4j/data"

  # Bind mount (for local backups)
  - ./neo4j/backups:/var/lib/neo4j/backups
```

### 4.3 Backup and Recovery Strategy

```bash
# Backup: Full database dump
docker exec docstratum-neo4j-prod \
  neo4j-admin database dump neo4j \
  --to-path=/var/lib/neo4j/backups/backup-$(date +%Y%m%d).dump

# Backup: Incremental (transaction log archival)
docker cp docstratum-neo4j-prod:/var/lib/neo4j/transactions \
  ./backups/transactions-$(date +%Y%m%d)/

# Restore: From dump
docker exec docstratum-neo4j-prod \
  neo4j-admin database load neo4j \
  --from-path=/var/lib/neo4j/backups/backup-20240115.dump \
  --overwrite-destination=true

# Automated backup script (cron job)
#!/bin/bash
BACKUP_DIR="/backups/neo4j"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)

docker exec docstratum-neo4j-prod \
  neo4j-admin database dump neo4j \
  --to-path=/var/lib/neo4j/backups/backup-${TIMESTAMP}.dump

# Retention: Remove backups older than 30 days
find ${BACKUP_DIR} -name "*.dump" -type f -mtime +${RETENTION_DAYS} -delete
```

### 4.4 Volume Cleanup Strategy

```bash
# List all volumes
docker volume ls | grep neo4j

# Remove unused volumes (after container deletion)
docker volume prune --filter label=version=dev

# Explicit volume removal (with backup first!)
docker exec docstratum-neo4j-dev \
  neo4j-admin database dump neo4j \
  --to-path=/var/lib/neo4j/backups/final-backup.dump

docker volume rm neo4j-data-dev

# Restore if needed
docker volume create neo4j-data-dev
docker run -v neo4j-data-dev:/data neo4j:5-community \
  neo4j-admin database load neo4j \
  --from-path=/var/lib/neo4j/backups/final-backup.dump
```

---

## 5. Environment Variable Configuration

### 5.1 Environment Variable Reference Table

| Variable | Default | Dev Value | Prod Value | Description |
|----------|---------|-----------|-----------|-------------|
| `NEO4J_AUTH` | `neo4j/password` | `neo4j/password123` | `neo4j/${NEO4J_PASSWORD}` | Authentication realm and password |
| `NEO4J_dbms_memory_heap_initial__size` | `512m` | `512m` | `2g` | Heap initial allocation |
| `NEO4J_dbms_memory_heap_max__size` | `1g` | `1g` | `4g` | Maximum heap size |
| `NEO4J_dbms_memory_pagecache_size` | `256m` | `256m` | `2g` | Page cache for graph store |
| `NEO4J_dbms_logs_query_enabled` | `false` | `true` | `false` | Query logging |
| `NEO4J_dbms_logs_query_threshold` | `0` | `0` | `1000` | Log queries slower than (ms) |
| `NEO4J_dbms_connector_bolt_connection__max` | `200` | `200` | `100` | Max concurrent connections |
| `NEO4J_dbms_connector_bolt_connection__idle__time__before__connection__timeout` | ∞ | ∞ | `900000` | Connection idle timeout (ms) |
| `NEO4J_dbms_ssl_policy_bolt_enabled` | `false` | `false` | `true` | Enable TLS on Bolt |
| `NEO4J_server_memory_off__heap__buffer__size` | `64m` | `64m` | `256m` | Off-heap buffer for I/O |
| `NEO4J_dbms_jvm_additional` | (none) | `-XX:+UseG1GC` | `-XX:+UseG1GC -XX:MaxGCPauseMillis=300` | JVM tuning flags |

### 5.2 Environment File Templates

**`.env.development`:**
```bash
# Neo4j Development Configuration
NEO4J_AUTH=neo4j/password123
NEO4J_dbms_memory_heap_initial__size=512m
NEO4J_dbms_memory_heap_max__size=1g
NEO4J_dbms_logs_query_enabled=true
COMPOSE_PROJECT_NAME=docstratum-dev
```

**`.env.production`:**
```bash
# Neo4j Production Configuration (SECRETS MANAGEMENT REQUIRED)
# Source from: AWS Secrets Manager, HashiCorp Vault, or K8s Secrets
NEO4J_PASSWORD=${VAULT_NEO4J_PASSWORD}
NEO4J_dbms_memory_heap_initial__size=2g
NEO4J_dbms_memory_heap_max__size=4g
NEO4J_dbms_logs_query_enabled=false
NEO4J_dbms_ssl_policy_bolt_enabled=true
COMPOSE_PROJECT_NAME=docstratum-prod
```

### 5.3 Loading Environment Files

```bash
# Using .env file
docker-compose --env-file .env.dev up -d

# Using multiple env files
docker-compose \
  --env-file .env.base \
  --env-file .env.dev \
  up -d

# Override specific variables
docker-compose \
  --env-file .env.prod \
  -e NEO4J_dbms_memory_heap_max__size=8g \
  up -d
```

---

## 6. Health Checks & Startup Verification

### 6.1 Health Check Configuration

```yaml
healthcheck:
  # Test: HTTP GET to browser endpoint
  test:
    - CMD
    - wget
    - --quiet
    - --tries=1
    - --spider
    - http://localhost:7474

  # Check every 5 seconds
  interval: 5s

  # Timeout after 3 seconds
  timeout: 3s

  # Retry up to 5 times
  retries: 5

  # Wait 10 seconds before first check (startup grace period)
  start_period: 10s
```

### 6.2 Advanced Health Check (Cypher Query)

```yaml
healthcheck:
  # Test: Execute simple Cypher query
  test:
    - CMD
    - cypher-shell
    - -u
    - neo4j
    - -p
    - password123
    - "RETURN 1 as status"

  interval: 10s
  timeout: 5s
  retries: 3
  start_period: 30s
```

### 6.3 Startup Verification Checklist

```bash
#!/bin/bash
# startup_verification.sh

echo "=== Neo4j Startup Verification ==="

# Wait for container to be running
echo "1. Checking container status..."
docker ps | grep docstratum-neo4j || exit 1
echo "   ✓ Container is running"

# Check health status
echo "2. Checking health status..."
HEALTH=$(docker inspect --format='{{.State.Health.Status}}' docstratum-neo4j-dev)
if [ "$HEALTH" == "healthy" ]; then
  echo "   ✓ Health check passed: $HEALTH"
else
  echo "   ✗ Health check failed: $HEALTH"
  exit 1
fi

# Test HTTP browser endpoint
echo "3. Testing HTTP browser endpoint..."
curl -s http://localhost:7474 > /dev/null && echo "   ✓ HTTP browser accessible" || exit 1

# Test Bolt protocol connection
echo "4. Testing Bolt protocol connection..."
cypher-shell -u neo4j -p password123 "RETURN 1" > /dev/null 2>&1 && \
  echo "   ✓ Bolt protocol accessible" || exit 1

# Check database state
echo "5. Checking database state..."
cypher-shell -u neo4j -p password123 "SHOW DATABASES" | grep neo4j && \
  echo "   ✓ Database 'neo4j' is online" || exit 1

# Get Neo4j version
echo "6. Neo4j version info..."
docker exec docstratum-neo4j-dev neo4j --version

echo "=== All checks passed! ==="
```

### 6.4 Startup Verification Execution

```bash
# Method 1: Using docker-compose wait
docker-compose up -d
docker-compose exec -T neo4j wget --quiet --tries=1 --spider http://localhost:7474
echo "Neo4j is ready"

# Method 2: Using custom script
docker-compose up -d
./startup_verification.sh

# Method 3: Using wait-for-it script
docker-compose up -d
./wait-for-it.sh localhost:7687 -- echo "Neo4j is ready"
```

---

## 7. Development vs. Production Configuration Comparison

### 7.1 Configuration Comparison Matrix

| Aspect | Development | Staging | Production |
|--------|-------------|---------|-----------|
| **Memory (Heap)** | 512m-1g | 1g-2g | 2g-4g |
| **Memory (Page Cache)** | 256m | 512m | 2g |
| **Query Logging** | Enabled | Conditional | Disabled |
| **Port Exposure** | 7474 + 7687 | 7687 only | 7687 via proxy |
| **TLS/SSL** | Disabled | Optional | Required |
| **Health Check** | HTTP GET | Cypher query | Cypher query |
| **Connection Limit** | 200 | 150 | 100 |
| **Restart Policy** | unless-stopped | on-failure:5 | on-failure:3 |
| **Volume Driver** | local | local | nfs/networked |
| **Resource Limits** | Permissive | Moderate | Strict |
| **GC Logging** | Disabled | Optional | Enabled |
| **Backup Strategy** | Manual | Daily | Hourly + WAL |

### 7.2 Quick-Start Commands

```bash
# Development setup
docker-compose -f docker-compose.dev.yml up -d
docker-compose -f docker-compose.dev.yml logs -f neo4j

# Staging setup
docker-compose -f docker-compose.yaml \
  --env-file .env.staging \
  up -d

# Production setup (with secrets)
docker-compose -f docker-compose.prod.yml up -d
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml exec neo4j \
  neo4j-admin database dump neo4j --to-path=/var/lib/neo4j/backups/

# Cleanup (development only)
docker-compose -f docker-compose.dev.yml down
docker volume prune
```

---

## Deliverables Checklist

- [ ] Docker Compose development configuration (docker-compose.dev.yml) created and tested
- [ ] Docker Compose production configuration (docker-compose.prod.yml) created with security hardening
- [ ] Docker Compose test configuration (docker-compose.test.yml) created for CI/CD
- [ ] Port mapping strategy documented with reference table
- [ ] Network architecture diagrams (ASCII) created for dev and prod
- [ ] Authentication strategy defined for dev and production
- [ ] Password management best practices documented
- [ ] TLS/SSL configuration examples provided
- [ ] Volume management and backup/recovery scripts created
- [ ] Environment variable configuration table completed
- [ ] Health check implementations documented with multiple approaches
- [ ] Startup verification checklist and scripts created
- [ ] Dev vs. Prod configuration comparison matrix completed
- [ ] All Docker Compose files validated for syntax
- [ ] Quick-start commands documented

---

## Acceptance Criteria

- [ ] `docker-compose up -d` successfully starts Neo4j in all environments
- [ ] Health checks pass within 30 seconds of container start
- [ ] Bolt protocol accessible at `bolt://localhost:7687` (dev/test)
- [ ] HTTP browser accessible at `http://localhost:7474` (dev/test)
- [ ] Authentication works with configured credentials
- [ ] Volumes persist data after container restart
- [ ] Memory allocation matches environment specifications
- [ ] Production config disables HTTP browser exposure
- [ ] TLS configuration validated for production
- [ ] Backup scripts create valid backups
- [ ] Environment files load correctly with `--env-file` flag
- [ ] All services referenced in other compose files start successfully
- [ ] Container logs provide clear startup and health status
- [ ] Port binding respects network isolation requirements
- [ ] Documentation includes troubleshooting steps for common issues

---

## Next Step

→ **v0.4.4c — Graph Population & Data Pipeline**

Implement the populate_neo4j.py script to extract data from the DocStratum loader and populate the Neo4j database with Concept nodes and DEPENDS_ON relationships.
