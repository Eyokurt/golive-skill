# Stage 08: Release & Rollback Readiness (Release & Rollback)

> **Objective**: Execute production deployments with zero downtime, ensure database schema changes remain backward-compatible, and maintain a battle-tested, single-command instant rollback mechanism capable of restoring service within minutes.

---

## 1. Action Items

### A. Zero-Downtime Deployment Strategies
- [ ] **Deployment Strategy Selection**: Choose and configure an appropriate deployment model:
  - *Blue/Green Deployment*: Parallel environments running current (Blue) and new (Green) versions; traffic switches instantaneously at the router level.
  - *Canary Deployment*: Route an initial slice (5-10%) of live traffic to the new version; observe error rates before graduating traffic to 100%.
  - *Rolling Update*: Incrementally update pods/nodes one by one; ensure new replicas pass health checks before receiving traffic.
- [ ] **Connection Draining**: Configure graceful draining timeouts (e.g., 30s) on terminating instances so in-flight HTTP requests complete without interruption.

### B. Backward-Compatible Database Migrations (Expand & Contract)
- [ ] **Two-Phase Compatibility**: Database migrations must remain fully compatible with both old and new application code versions simultaneously:
  - Never drop or rename columns directly in a live database.
  - Phase 1 (Expand): Add new columns or tables; update application code to write to both old and new schemas.
  - Phase 2 (Contract): After the new version is fully running and verified, deploy a subsequent migration to remove obsolete columns.
- [ ] **Down Migration Verification**: Test reversible rollback scripts (`down` migrations) in staging prior to production execution.

### C. Post-Deployment Smoke Testing & Verification
- [ ] **Automated Smoke Tests**: Execute automated verification scripts against core endpoints immediately upon rollout completion.
- [ ] **Version Introspection**: Query `/version` or `/build-info` endpoints to verify that active instances run the expected commit SHA and release tag.

### D. Tested Instant Rollback Procedure
- [ ] **Objective Rollback Triggers**: Establish clear, metric-driven rollback thresholds rather than subjective decisions:
  - Error rate: Sustained HTTP 5xx > 1% during the first 5 minutes post-deployment.
  - Latency: p95 latency doubles compared to pre-release baselines.
  - Functional breakdown: Critical user flows (login, payments) fail smoke tests.
- [ ] **Single-Command Execution**: Rollbacks must be executable via a single CLI command or pipeline trigger within 3 minutes.
- [ ] **Incident Communication Plan**: Clearly designate who has rollback authority and define the communications channel for release status updates.

---

## 2. Exit Gate (Final Go-Live Gate)

The deployment cannot be declared **LIVE** until **all** of the following criteria are satisfied:
1. All Stage 08 checklist items are completed in `GOLIVE.md`.
2. A simulated rollback drill has been executed cleanly in staging, restoring the previous stable release without manual intervention.
3. Automated post-deployment smoke tests pass with zero errors in production.
4. Error rates and latency metrics remain within normal baseline parameters for at least 15 minutes post-launch.

---

## 3. Rationale

| Action Item | Why It Is Mandatory |
|:---|:---|
| Expand & Contract Pattern | During rolling deployments, old and new application versions query the database concurrently. Dropping a column immediately causes the older version to crash, making instant rollbacks impossible. |
| Automated Smoke Tests | Enables teams to detect critical regressions within 10 seconds of deployment rather than waiting for customer complaints. |
| Single-Command Rollback | In high-stress outage scenarios, complex multi-step manual rollback procedures are prone to catastrophic operator error. |
| Objective Rollback Criteria | Eliminates hesitation and debating ("let's wait and see if it recovers") by defining clear parameters for aborting problematic releases. |

---

## 4. Common Pitfalls

- ❌ **Irreversible Schema Migrations**: Dropping columns or changing column types without backward compatibility, permanently breaking rollback capability (Data Lock-in).
- ❌ **Deploying on Friday Afternoons**: Releasing changes when support and engineering availability is lowest.
- ❌ **Never Testing Rollbacks**: Discovering during a live outage that the rollback script fails due to permission errors or missing previous build artifacts.
- ❌ **Instant 100% Traffic Cutover**: Cutting over 100% of live traffic immediately without canary verification during major architectural rewrites.
