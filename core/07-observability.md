# Stage 07: Observability & Telemetry (Observability)

> **Objective**: Enable engineering teams to understand the internal health of production systems through external telemetry (structured logs, metrics, distributed traces, and actionable alerts), reducing Mean Time to Detect (MTTD) and Mean Time to Resolve (MTTR) to minutes.

---

## 1. Action Items

### A. Structured JSON Logging
- [ ] **Standardized JSON Output**: Format all console and file log outputs as single-line JSON objects containing `timestamp`, `level`, `message`, `service`, and `context`.
- [ ] **Correlation & Trace Propagation**: Generate a unique `x-request-id` or OpenTelemetry `trace_id` for every inbound HTTP/gRPC request; propagate it across downstream RPC calls, background queues, and database queries.
- [ ] **PII Masking**: Automatically sanitize and redact Personally Identifiable Information (PII)—including passwords, credit card numbers, national identification numbers, and bearer tokens—before log lines are emitted.

### B. The Four Golden Signals
- [ ] **Traffic**: Measure incoming request volume via Requests Per Second (RPS).
- [ ] **Errors**: Track failure rates via HTTP 5xx responses and unhandled exception frequencies.
- [ ] **Latency**: Track request duration percentiles across p50, p95, and p99 distributions.
- [ ] **Saturation**: Monitor CPU utilization, memory pressure, disk consumption, and database connection pool saturation (alerting at > 80% capacity).

### C. AI / LLM Telemetry & Cost Tracking
- [ ] **Token Consumption**: Record prompt and completion token counts per request and session.
- [ ] **Cost Accounting**: Calculate real-time cumulative expenses ($/day, $/service) per provider and model.
- [ ] **Model Latency & Provider Reliability**: Track Time-To-First-Token (TTFT), total streaming duration, and upstream provider 429/500 error rates.
- [ ] **User Feedback Tracking**: Log user feedback events (thumbs up/down ratings, explicit corrections) tied to specific generation IDs.

### D. Actionable Alerting Rules & On-Call Routing
- [ ] **Critical Threshold Alerts**:
  - Error Rates: Sustained HTTP 5xx > 1% over a 5-minute rolling window.
  - Latency: p95 response time > 1500ms sustained for 3 minutes.
  - System Resources: Available disk space < 15% or RAM consumption > 85%.
  - AI Budget: Projected or daily spend reaching 80% of defined budget caps.
- [ ] **Notification Channels**: Direct critical alerts to on-call engineers via Slack, Discord, or PagerDuty; ensure every alert includes an incident summary and a direct link to the operational runbook.

---

## 2. Exit Gate (Gate 07)

Stage 08 cannot commence until **all** of the following criteria are satisfied:
1. All Stage 07 checklist items are completed in `GOLIVE.md`.
2. Verified that sample test requests produce structured JSON logs with identical, propagating `trace_id` values in the centralized log aggregator (Datadog, Loki, CloudWatch).
3. Triggering a synthetic 500 error or simulated latency spike delivers an alert notification to the designated incident channel.
4. LLM token consumption and cost monitoring dashboards actively visualize incoming telemetry.

---

## 3. Rationale

| Action Item | Why It Is Mandatory |
|:---|:---|
| Structured JSON Logs | Querying millions of plain-text log lines during an outage is impossible. JSON logs allow instant filtering and aggregation across distributed systems. |
| Trace & Correlation IDs | In distributed microservices, correlation IDs provide the only reliable way to trace a failed user journey across multiple backend services. |
| Saturation Monitoring | When a disk reaches 100% capacity, databases crash and corrupt data. Alerting at 85% provides time to remediate before catastrophic failure. |
| LLM Cost Alarms | Runaway prompt loops or scraping attacks can run up tens of thousands of dollars in LLM API bills overnight if cost alarms are absent. |

---

## 4. Common Pitfalls

- ❌ **Alert Fatigue**: Flooding on-call channels with non-actionable warning notifications, causing engineers to ignore genuine crisis alerts.
- ❌ **Logging Cleartext PII**: Recording customer emails, passwords, or personal data into log streams, leading to GDPR/compliance violations.
- ❌ **Focusing Exclusively on CPU**: Assuming a system is healthy because CPU utilization is low, while thread pools or database connections are completely starved.
- ❌ **Never Testing Alert Destinations**: Creating alert rules without testing delivery, only to discover during an incident that alerts were routed to an unmonitored inbox.
