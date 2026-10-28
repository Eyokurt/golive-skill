# Stage 02: Quality & Evaluation (Quality & Eval)

> **Objective**: Prove business logic correctness, regression resilience, and performance boundaries before exposing the system to production traffic. Bridge conventional automated software testing with behavioral evaluation (evals) for AI and LLM components.

---

## 1. Action Items

### A. Unit & Integration Testing
- [ ] **Unit Tests**: Core algorithms, utility functions, and data transformations must be tested in isolation using lightweight mocks with zero test failures.
- [ ] **Integration Tests**: Database queries, messaging queues, and API controllers must be validated against real or ephemeral test containers (e.g., Testcontainers) rather than in-memory SQLite mocks.
- [ ] **Code Coverage**: Target at least 80% coverage on core domain logic, with 100% coverage on critical authentication, payment, and data destruction pathways.

### B. End-to-End (E2E) & Smoke Testing
- [ ] **Critical User Flows**: Automate end-to-end tests (via Playwright, Cypress, or comprehensive API suites) for registration, login, primary feature execution, and billing workflows.
- [ ] **Negative Scenarios**: Test invalid payloads, expired tokens, oversized files, and unauthorized access attempts to ensure the system consistently responds with appropriate HTTP 4xx status codes.

### C. AI / LLM Golden Evaluation Suite
- [ ] **Golden Dataset**: Maintain a version-controlled evaluation dataset containing at least 50-100 representative input-output pairs capturing standard usage and edge cases.
- [ ] **Regression & Quality Metrics**:
  - Structural Integrity: 100% compliance with expected JSON output schemas.
  - Semantic Accuracy: Measure accuracy, precision, and recall against predefined quality thresholds (e.g., >= 90%).
  - Safety & Toxicity: Automated checks for hallucination, prompt injection vulnerability, and harmful outputs.
- [ ] **Baseline Comparison**: Updated prompt templates or newer model versions must not score below established performance baselines.

### D. Performance, Latency & Load Benchmarking
- [ ] **Latency Budgets**:
  - Backend API p95 response time < 250ms (excluding non-streaming LLM calls).
  - LLM Time-To-First-Token (TTFT) < 1200ms; total response duration p95 < 6s.
- [ ] **Load & Stress Testing**: Benchmark the system using tools like k6, Locust, or Hey at 1.5x expected peak concurrent load, monitoring memory stability, CPU saturation, and error rates.

---

## 2. Exit Gate (Gate 02)

Stage 03 cannot commence until **all** of the following criteria are satisfied:
1. All Stage 02 checklist items are completed in `GOLIVE.md`.
2. Clean CI or local test reports verifying 100% passing unit and integration test suites.
3. The AI Golden Dataset evaluation passes with zero schema violations and scores above established accuracy thresholds.
4. Stress testing confirms a 5xx error rate < 0.1% and p95 latency remains within SLA limits under 1.5x peak load.

---

## 3. Rationale

| Action Item | Why It Is Mandatory |
|:---|:---|
| Containerized Integration Testing | Tests that pass on SQLite often fail in production against PostgreSQL due to dialect variations, locking mechanisms, or transaction isolation semantics. |
| Golden Evaluation Dataset | Subtle prompt phrasing changes can introduce a 30% drop in accuracy on domain edge cases without being apparent in casual manual checks. |
| Negative Path Testing | Testing only the happy path leaves systems vulnerable to unhandled exceptions when encountering unexpected or malicious inputs. |
| Load & Latency Benchmarks | Discovering database connection pool limits when 20 concurrent users arrive in production results in immediate downtime. |

---

## 4. Common Pitfalls

- ❌ **Testing Only Happy Paths**: Verifying valid inputs while neglecting network partitions, empty responses, or 429 rate limits.
- ❌ **Calling Live Paid APIs in Unit Tests**: Pointing unit tests to production OpenAI or Stripe endpoints causes billing spikes, flakiness, and CI delays.
- ❌ **Failing to Update the Eval Suite**: Not incorporating real-world production edge cases back into the regression dataset (broken feedback loop).
- ❌ **Relying Exclusively on Average Latency**: Assuming a 200ms average response time is acceptable while the p99 percentile forces users to wait over 8 seconds.
