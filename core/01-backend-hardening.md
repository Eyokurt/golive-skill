# Stage 01: Backend Hardening

> **Objective**: Prepare the backend service to withstand production workloads, upstream outages, and hostile inputs; ensure the service reliably self-reports operational health, and place all AI/LLM integrations under strict cost, timeout, and fallback controls.

---

## 1. Action Items

### A. Configuration & Startup Validation
- [ ] **Fail-Fast Bootstrapping**: At application startup, all environment variables (`process.env` / `os.environ`) must be validated against a strict schema (Pydantic, Zod, Envalid). If any mandatory variable is missing or fails type validation, the application must abort immediately (`exit 1`).
- [ ] **Environment Separation**: Ensure debug flags (`DEBUG=False`), local development mock services, and ephemeral test databases are strictly disabled in production.

### B. Error Handling & Resilience
- [ ] **Centralized Global Exception Handler**: Catch all unhandled exceptions at a single application boundary. Never return raw stack traces or internal database error messages to users; emit generic error codes and attach a Correlation ID.
- [ ] **Connection Pools & Strict Timeouts**: Configure explicit connection and read timeouts on database connections, Redis pools, and all external HTTP calls (connect timeout: max 2s, read timeout: max 5s). Set explicit connection pool ceilings.
- [ ] **Graceful Shutdown**: Listen for `SIGTERM` and `SIGINT` signals from the operating system/orchestrator. Stop accepting incoming traffic, allow active requests a drain window (e.g., 10-15s) to complete, and close connection pools cleanly.

### C. Health & Readiness Probes
- [ ] **Liveness Probe (`/healthz`)**: Indicates whether the process is alive (lightweight check; performs no database or upstream queries).
- [ ] **Readiness Probe (`/readyz`)**: Confirms whether the process is ready to receive traffic (verifies database connectivity, cache reachability, and message broker status). Must return HTTP 503 if any required upstream dependency is unavailable.

### D. Authentication & Authorization (AuthN / AuthZ)
- [ ] Enforce JWT/session validation on all protected endpoints; reject expired or invalid tokens with HTTP 401.
- [ ] Apply role-based and attribute-based access control (RBAC/ABAC) at the controller or service layer.

### E. AI & LLM Hardening
- [ ] **Prompt & Model Versioning**: Do not hardcode prompt templates or model identifiers in application code. Manage them through dynamic, versioned configurations or an external registry.
- [ ] **Fallback Model & Circuit Breaker**: If the primary LLM provider fails (HTTP 5xx or rate limiting), route requests to a secondary fallback model via an automated circuit breaker.
- [ ] **Request Timeouts & Exponential Backoff**: Impose a hard ceiling on model request durations (e.g., 30s for streaming) and limit retries to 2-3 attempts using exponential backoff with jitter.
- [ ] **Per-User / Per-Session Token & Cost Limits**: Enforce token rate limits and cost budget caps per user to prevent abuse and unexpected billing spikes.

---

## 2. Exit Gate (Gate 01)

Stage 02 cannot commence until **all** of the following criteria are satisfied:
1. All Stage 01 checklist items are completed in `GOLIVE.md`.
2. Bootstrapping with a missing mandatory environment variable verified to fail fast with non-zero exit code (`exit code != 0`).
3. `/healthz` returns HTTP 200, while a simulated database disconnection causes `/readyz` to immediately return HTTP 503.
4. Exceeding token or cost limits on LLM endpoints verified to return HTTP 429 Too Many Requests.

---

## 3. Rationale

| Action Item | Why It Is Mandatory |
|:---|:---|
| Fail-Fast Configuration | An unvalidated secret or missing configuration that triggers a runtime `KeyError` during user interaction leads to data corruption and service degradation. |
| Global Exception Handler | Exposing raw stack traces gives attackers insight into internal file structures, database schemas, and vulnerable dependency versions (CWE-209). |
| Readiness Probe Separation | If readiness is not checked, orchestrators route traffic to pods before connections are established, resulting in avoidable 502/503 errors. |
| Graceful Shutdown | Abruptly terminating pods mid-transaction leaves database operations in an inconsistent state and corrupts user data. |
| LLM Fallbacks & Cost Limits | Upstream provider outages halt entire workflows unless a fallback is present. Uncapped token limits allow runaway loops or scrapers to incur thousands of dollars in fees within minutes. |

---

## 4. Common Pitfalls

- ❌ **Leaving `DEBUG=True` Enabled**: Exposing internal stack traces and environment details to production clients.
- ❌ **Coupling Liveness to Database Health**: Running database queries in `/healthz`. A momentary database slowdown causes the load balancer or Kubernetes to kill all healthy app pods simultaneously (cascading failure).
- ❌ **Unbounded Outbound HTTP Requests**: Making network calls without timeouts; an upstream stall locks application worker threads indefinitely.
- ❌ **Consuming LLM Outputs Without Validation**: Passing unstructured model outputs directly to business logic without schema validation (creating Prompt Injection and hallucination vulnerabilities).
