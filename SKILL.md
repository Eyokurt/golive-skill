---
name: golive-skill
description: Use when preparing, auditing, executing, or tracking a production go-live, deployment, or release across backend, frontend, and cloud/on-prem/edge environments. Trigger with "deploy", "canlıya alma", "go-live", "production release", "production'a çıkış", "release checklist", "deployment gate".
---

# Go-Live Orchestration & Release Skill (`golive-skill`)

This skill systematically orchestrates the **Backend → Quality & Eval → Frontend → Packaging → CI/CD → Security → Observability → Release & Rollback** lifecycle. It persists execution state in a repository-level `GOLIVE.md` tracker file and strictly enforces exit gates before allowing progression to subsequent phases.

---

## 🔒 Non-Negotiable Safety Protocols (Prime Rules)

Agents executing this skill must **never violate** the following three rules:

1. **Safety Brake on Destructive Actions**:
   - Irreversible actions—such as dropping tables/columns, executing data migrations, stopping running production pods/containers, modifying DNS records, or applying infrastructure updates (`terraform apply`, `helm upgrade`)—require a comprehensive impact analysis presented to the user and **explicit confirmation** before execution.
2. **Zero-Secrets-in-Code Mandate**:
   - Passwords, API tokens, private keys, and certificates must never be committed to code, PR descriptions, commit messages, or written into `GOLIVE.md`. Manage secrets strictly via Vault, KMS, or ephemeral runtime injections.
3. **Environment & Context Verification**:
   - Before executing any command, verify active context (`$env:NODE_ENV`, `kubectl config current-context`, `aws sts get-caller-identity`, target database hostname) to ensure actions are never run against the wrong account or cluster.

---

## 🔄 Lifecycle & Execution Flow

```
[Start]
   │
   ▼
1. Read / Initialize GOLIVE.md (from assets/GOLIVE.template.md)
   │
   ▼
2. Identify Target Fields (Cloud/SaaS, Customer On-Prem, Edge/Device)
   │
   ▼
3. Run Pre-Audit (execute scripts/audit.py and mark pre-existing items)
   │
   ▼
4. Sequentially Execute Core Stages (core/01 -> core/08)
   │   ├─ Each stage enforces strict Exit Criteria (Gate)
   │   └─ DO NOT advance until gate conditions are verified
   │
   ▼
5. Execute Selected Field Branches (fields/)
   │
   ▼
6. Update GOLIVE.md Status & Announce LIVE
```

---

## 📋 Step-by-Step Execution Guide

### Step 1: Initialize / Read State (`GOLIVE.md`)
1. Check repository root for `GOLIVE.md`.
2. If **absent**:
   - Load `assets/GOLIVE.template.md`.
   - Populate project metadata, timestamp, and target fields; write to repo root as `GOLIVE.md`.
3. If **present**:
   - Read `GOLIVE.md`; load current stage, completed gates, and pending checklist items into context.

### Step 2: Determine Target Deployment Field(s)
Confirm the target operational environment(s) (can be multiple):
- ☁️ **Cloud / SaaS**: AWS, GCP, Azure, Kubernetes, Serverless, multi-tenant architectures.
- 🏢 **Customer On-Premises**: Enterprise data centers, customer VPCs, air-gapped offline networks.
- 🤖 **Edge / Device**: NVIDIA Jetson, Raspberry Pi, ARM64 industrial IPCs, robotics, IoT devices.

### Step 3: Automated Repository Pre-Audit
Scan the codebase for existing production assets rather than searching manually:
```powershell
python <path_to_skill>/scripts/audit.py --path . --sync
```
This script audits Dockerfiles, test suites, CI pipelines, secret exposures, and health endpoints, automatically checking off detected items in `GOLIVE.md`.

---

## 🚪 Core Stages & Exit Gates

Consult the respective guide for each phase and verify its blocking gate criteria:

| No | Stage File | Primary Focus | Blocking Exit Gate Criteria |
|:---|:---|:---|:---|
| **01** | [`core/01-backend-hardening.md`](file:///core/01-backend-hardening.md) | Config schema validation, fail-fast init, global error handler, `/healthz` & `/readyz`, graceful shutdown, LLM token/cost limits & fallback model. | Missing env variable triggers immediate process exit; simulated DB outage causes `/readyz` to return HTTP 503; LLM budget breach returns 429. |
| **02** | [`core/02-quality-and-eval.md`](file:///core/02-quality-and-eval.md) | Unit & integration tests, E2E critical user flows, Golden eval dataset, latency budgets & load benchmark. | 100% passing tests; zero JSON schema violations on AI eval set; p95 latency adheres to SLA under 1.5x peak load. |
| **03** | [`core/03-frontend-readiness.md`](file:///core/03-frontend-readiness.md) | Zero-error production build, bundle optimization (<200KB initial), asset caching, 4-state components, Error Boundaries, Anti-AI-Slop standards. | `npm run build` succeeds without type/lint errors; network disconnection does not cause blank screen; zero UI chrome emojis. |
| **04** | [`core/04-packaging.md`](file:///core/04-packaging.md) | Multi-stage Dockerfile, non-root execution (`USER`), pinned lockfiles, `.dockerignore`, image CVE scanner. | Container runs as non-root user (`whoami != root`); Trivy/Grype reports zero CRITICAL CVEs. |
| **05** | [`core/05-ci-cd.md`](file:///core/05-ci-cd.md) | Automated sequential pipeline (Lint -> Test -> Build -> Scan), OIDC cloud auth, branch protection rules, manual production gate. | CI pipeline completes cleanly; direct push to main branch is blocked; production deploy requires manual sign-off. |
| **06** | [`core/06-security-and-secrets.md`](file:///core/06-security-and-secrets.md) | Secret scanning (gitleaks), KMS/Vault secret management, restricted CORS, CSP/HSTS headers, auth rate limiting. | Git history clean of secrets (0 leaks); zero CRITICAL/HIGH dependencies; wildcard CORS rejected. |
| **07** | [`core/07-observability.md`](file:///core/07-observability.md) | Structured JSON logging, Correlation/Trace IDs, 4 golden signals, LLM telemetry & cost tracking, actionable alerting rules. | Test request logs appear formatted as JSON with matching trace_id; simulated alarm reaches designated notification channel. |
| **08** | [`core/08-release-and-rollback.md`](file:///core/08-release-and-rollback.md) | Zero-downtime deployment (Blue/Green, Rolling), backward-compatible DB migrations (expand/contract), automated smoke tests, single-command rollback. | Rollback drill verified in staging; post-deploy smoke tests pass with 0 errors; error rate stable for 15 mins post-launch. |

---

## 🌐 Field Branches

After completing the core stages, execute the specific checklist for each designated field:

1. ☁️ **Cloud / SaaS**:
   - Guide: [`fields/cloud-saas.md`](file:///fields/cloud-saas.md)
   - Focus: Terraform/IaC drift audit, DNS TTL reduction, automated TLS renewal, Kubernetes HPA & resource limits, cloud budget alerts, Canary routing.
2. 🏢 **Customer On-Premises (Enterprise & Air-Gapped)**:
   - Guide: [`fields/customer-onprem.md`](file:///fields/customer-onprem.md)
   - Focus: Self-contained offline distribution bundle, air-gapped installation verification, enterprise proxy & custom root CA support, offline cryptographic licensing, support dump diagnostics script, zero external telemetry (GDPR/KVKK compliance).
3. 🤖 **Edge / Device (Embedded & IoT)**:
   - Guide: [`fields/edge-device.md`](file:///fields/edge-device.md)
   - Focus: Target architecture cross-compilation (ARM64/Jetson), offline-first local persistence (SQLite/RocksDB) with store-and-forward sync, dual-partition A/B OTA recovery (anti-brick), hardware watchdog, flash memory endurance (`tmpfs` logging), and thermal resilience.

---

## 📝 State Updates & Completion Rules

- Upon completing each stage:
  1. Check off finished items `[x]` in `GOLIVE.md`.
  2. Document date, approver, and verification artifacts (test reports, image hashes, links) under the "Exit Gate" section.
  3. Advance `Current Stage` metadata to the next phase.
- Once Stage 08 and all designated Field Gates are approved:
  - Transition `Release Status` to `LIVE`.
  - Issue the final go-live report with monitoring dashboard links.
