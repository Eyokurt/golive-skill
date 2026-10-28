# Go-Live State Tracker (`GOLIVE.md`)

> **State File Protocol**: This document serves as the official state record for the go-live lifecycle. Stages are checked off sequentially as exit criteria are verified. Progression to subsequent stages is blocked until the active gate is fulfilled.

---

## 📌 Project & Release Metadata

- **Project Name**: [PROJECT_NAME]
- **Target Release / Tag**: `v1.0.0`
- **Target Deployment Fields**:
  - [ ] Cloud / SaaS
  - [ ] Customer On-Premises (Enterprise)
  - [ ] Edge / Device (Embedded / IoT)
- **Start Date**: YYYY-MM-DD
- **Last Updated**: YYYY-MM-DD HH:MM
- **Release Engineer / Owner**: @operator
- **Current Stage**: `01-backend-hardening`
- **Release Status**: `IN_PROGRESS` <!-- PENDING | IN_PROGRESS | GATE_BLOCKED | READY_FOR_DEPLOY | LIVE | ROLLED_BACK -->

---

## 🚦 Exit Gates Summary

| No | Stage Name | Scope | Status | Approver / Date |
|:---|:---|:---|:---:|:---|
| 01 | Backend Hardening | All | 🟡 IN_PROGRESS | - |
| 02 | Quality & Eval | All | ⚪ QUEUED | - |
| 03 | Frontend Readiness | All / Applicable | ⚪ QUEUED | - |
| 04 | Packaging & Containerization | All | ⚪ QUEUED | - |
| 05 | CI/CD Pipeline | All | ⚪ QUEUED | - |
| 06 | Security & Secret Management | All | ⚪ QUEUED | - |
| 07 | Observability & Telemetry | All | ⚪ QUEUED | - |
| 08 | Release & Rollback Readiness | All | ⚪ QUEUED | - |
| F1 | Field Extension: Cloud / SaaS | Cloud | ⚪ QUEUED | - |
| F2 | Field Extension: Customer On-Prem | On-Prem | ⚪ QUEUED | - |
| F3 | Field Extension: Edge / Device | Edge | ⚪ QUEUED | - |

*(Status Indicators: 🟢 PASSED, 🟡 IN_PROGRESS, 🔴 BLOCKED, ⚪ QUEUED, 🔘 OUT_OF_SCOPE)*

---

## 🛠️ Core Stages Checklist

### Stage 01: Backend Hardening
> Reference: `core/01-backend-hardening.md`
- [ ] Environment variables validated via strict schemas (Zod / Pydantic / Envalid) at startup; fails fast on invalid/missing config.
- [ ] Centralized global exception handler active; suppresses raw stack traces and internal SQL details.
- [ ] Authentication and authorization (AuthN/AuthZ) middleware enforced on protected routes with signature verification.
- [ ] `/healthz` (liveness) and `/readyz` (readiness with DB/Redis/upstream checks) probes exposed.
- [ ] Graceful shutdown handlers (`SIGTERM`/`SIGINT`) active; in-flight requests and connection pools drained cleanly.
- **AI/LLM Specific Items**:
  - [ ] Prompt templates and model identifiers decoupled from code and loaded dynamically from versioned configuration.
  - [ ] Hard request timeouts, exponential backoff retries, and a fallback circuit breaker configured for LLM endpoints.
  - [ ] Per-user and per-session token and budget limits (cost rate limiting) enforced.
- **Exit Gate (Gate 01)**:
  - Status: `[ ] APPROVED`
  - Evidence / Log Output: 

---

### Stage 02: Quality & Eval
> Reference: `core/02-quality-and-eval.md`
- [ ] Unit and integration test suites passing cleanly (0 failures).
- [ ] Critical end-to-end (E2E) user flows verified via automated suites.
- [ ] AI / RAG regression Golden Dataset evaluated; satisfies baseline accuracy and format constraints.
- [ ] Service latency and throughput benchmarks (p95 / p99 latency) satisfy production SLA targets under load.
- **Exit Gate (Gate 02)**:
  - Status: `[ ] APPROVED`
  - Test Report Link / Summary: 

---

### Stage 03: Frontend Readiness
> Reference: `core/03-frontend-readiness.md`
- [ ] Production build (`npm run build` / `vite build`) completes cleanly with 0 type and lint errors.
- [ ] Bundle size and route-based code splitting optimized; heavy dependencies eliminated.
- [ ] Static assets served with content hashes and long-lived immutable cache headers; `index.html` configured with `no-cache`.
- [ ] 4-state component architecture verified: Loading skeleton, Empty state, Error state (with retry), Interactive states.
- [ ] Error boundaries isolate runtime component crashes without causing full-screen blank pages.
- [ ] Graceful fallback / offline message displayed when upstream backend API is unavailable.
- **Exit Gate (Gate 03)**:
  - Status: `[ ] APPROVED`
  - Build Output Bundle Size: 

---

### Stage 04: Packaging & Containerization
> Reference: `core/04-packaging.md`
- [ ] Multi-stage `Dockerfile` separates build-time tooling from the minimal runtime image.
- [ ] Container runs as an unprivileged, non-root user (`UID != 0`).
- [ ] Dependencies pinned and installed from locked manifests (`package-lock.json`, `poetry.lock`, `uv.lock`).
- [ ] Container image scanned for vulnerabilities (Trivy / Grype / Snyk - 0 CRITICAL CVEs).
- [ ] `.dockerignore` comprehensively excludes `.git`, `.env`, local artifacts, and test files.
- **Exit Gate (Gate 04)**:
  - Status: `[ ] APPROVED`
  - Container Image Digest / Size: 

---

### Stage 05: CI/CD Pipeline
> Reference: `core/05-ci-cd.md`
- [ ] Automated pipeline triggers on every PR and merge (Lint -> Test -> Build -> Vulnerability Scan).
- [ ] Strict environment isolation maintained; cloud credentials authenticated via short-lived OIDC roles.
- [ ] Main branch protected with mandatory branch protection rules (at least 1 PR review + passing CI checks).
- [ ] Production deployment requires explicit manual approval.
- **Exit Gate (Gate 05)**:
  - Status: `[ ] APPROVED`
  - Pipeline Execution Run ID / URL: 

---

### Stage 06: Security & Secret Management
> Reference: `core/06-security-and-secrets.md`
- [ ] Repository and commit history scanned for exposed credentials (gitleaks / trufflehog clean).
- [ ] Production secrets managed dynamically through an external vault (AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager).
- [ ] Strict CORS origin policy enforced (wildcard `*` explicitly prohibited).
- [ ] Standard HTTP security headers active (CSP, HSTS, X-Content-Type-Options, X-Frame-Options).
- [ ] API rate limiting and brute-force protection enabled on sensitive endpoints.
- **Exit Gate (Gate 06)**:
  - Status: `[ ] APPROVED`
  - Security Scan Summary: 

---

### Stage 07: Observability & Telemetry
> Reference: `core/07-observability.md`
- [ ] Structured single-line JSON logging standardized with propagated Correlation / Trace IDs.
- [ ] Four Golden Signals collected: Traffic (RPS), Errors (5xx rate), Latency (p50/p95/p99), Saturation (CPU/RAM/Pool).
- [ ] LLM telemetry active: Prompt/completion token counts, real-time cost ($/day), provider error rates, TTFT.
- [ ] Alerting rules configured with actionable thresholds (e.g. 5xx > 1% over 5m, disk space < 15%) routed to on-call channels.
- **Exit Gate (Gate 07)**:
  - Status: `[ ] APPROVED`
  - Dashboard & Alert Links: 

---

### Stage 08: Release & Rollback Readiness
> Reference: `core/08-release-and-rollback.md`
- [ ] Zero-downtime deployment strategy verified (Blue/Green, Rolling update with connection draining).
- [ ] Single-command instant rollback drill executed successfully in staging (< 3 minutes recovery).
- [ ] Database schema migrations designed with backward compatibility (expand-and-contract pattern).
- [ ] Automated post-deployment smoke tests ready to execute immediately upon release.
- **Exit Gate (Gate 08)**:
  - Status: `[ ] APPROVED`
  - Verified Rollback Command: 

---

## 🌐 Field Branches

### Field F1: Cloud / SaaS
> Reference: `fields/cloud-saas.md` (Applicable if Cloud deployment is selected)
- [ ] All infrastructure declared as code (Terraform / Pulumi / CDK); no manual console drift.
- [ ] DNS records configured with reduced TTL (60-300s); automated TLS renewal verified with HSTS.
- [ ] Horizontal Pod Autoscaler (HPA) and explicit container resource requests/limits configured.
- [ ] Cloud budget alert thresholds ($50%, 80%, 100%) active with notifications.
- [ ] Canary or weighted traffic routing configured at the ingress level.
- **Gate Status**: `[ ] APPROVED`

---

### Field F2: Customer On-Premises (Enterprise & Air-Gapped)
> Reference: `fields/customer-onprem.md` (Applicable if On-Premises deployment is selected)
- [ ] Single-command offline installation bundle (Helm chart / Docker Compose tarball) verified.
- [ ] Complete air-gapped installation tested with zero public internet connectivity.
- [ ] Corporate HTTP proxy and custom internal Root CA certificate injection supported.
- [ ] Offline cryptographic licensing verification and capacity limits tested.
- [ ] GDPR / privacy compliance verified: zero external telemetry, sanitized support dump tool provided.
- **Gate Status**: `[ ] APPROVED`

---

### Field F3: Edge / Device (Embedded & IoT)
> Reference: `fields/edge-device.md` (Applicable if Edge / Device deployment is selected)
- [ ] Target architecture cross-compilation (ARM64, Jetson, RPi) and hardware acceleration drivers verified.
- [ ] Robust offline-first operation verified with local embedded storage (SQLite/RocksDB) and store-and-forward sync.
- [ ] Dual-partition A/B OTA update mechanism with automatic fallback recovery (anti-brick) verified.
- [ ] Memory ceiling enforced; logs redirected to RAM (`tmpfs`); thermal throttling resilience tested.
- [ ] Hardware/software watchdog timer and power-loss recovery verified.
- **Gate Status**: `[ ] APPROVED`

---

## 🚨 Emergency Incident & Rollback Runbook

If critical failure occurs post-deployment:
1. **Rollback Trigger Conditions**:
   - 5xx error rate > 2% sustained for 3 minutes.
   - Database connection pool exhaustion / deadlock.
   - Primary user workflow (authentication, checkout, core processing) failing smoke tests.
2. **Instant Rollback Commands**:
   - Kubernetes: `kubectl rollout undo deployment/<DEPLOYMENT_NAME> -n <NAMESPACE>`
   - Docker Compose: `docker compose -f docker-compose.prod.yml down && docker compose -f docker-compose.prod.yml up -d --build <PREVIOUS_IMAGE>`
   - Terraform: `terraform apply -var="image_tag=vPREVIOUS"`
3. **Escalation Channel**: Dedicated release or incident triage channel.
