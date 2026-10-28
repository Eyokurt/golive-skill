# Field Extension: Customer On-Premises (Enterprise & Air-Gapped)

> **Objective**: Address installation packaging, enterprise networking, offline air-gapped readiness, cryptographic licensing, diagnostic support, and strict data privacy (GDPR / KVKK) requirements when deploying software into customer-managed data centers or isolated virtual private clouds.

---

## 1. Action Items

### A. Distribution Packaging & Portability
- [ ] **Self-Contained Installer**: Provide an automated installer packaged as a Helm chart, Docker Compose bundle, or single standalone binary.
- [ ] **Air-Gapped Installation**: Support completely offline environments where outbound internet access is blocked. Bundle all container images and dependencies into a single offline tarball (`docker save` / offline Helm archive) loadable into local registries.
- [ ] **Pre-Flight Validation Script**: Ship a standalone `precheck.sh` script to validate host CPU, RAM, disk space, kernel parameters, and container engine versions prior to installation.

### B. Enterprise Networking & Proxy Constraints
- [ ] **Corporate Proxy & Custom CA Support**: Support enterprise outbound HTTP/HTTPS proxies (`HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`) and permit the injection of internal enterprise Root CA certificates.
- [ ] **Strict Port Minimization**: Expose only documented, necessary service ports (e.g., standard 443 and 80); eliminate random high-port bindings.

### C. Offline Cryptographic Licensing
- [ ] **Air-Gapped License Validation**: Validate cryptographically signed (asymmetric RSA/ECDSA) license files offline without requiring outbound connectivity to a remote validation server.
- [ ] **Enforced Capacity Limits**: Gracefully enforce limits on user counts, CPU core counts, or expiration dates; display advance warnings prior to license expiration.

### D. Diagnostics & Support Tooling
- [ ] **Support Bundle Generator**: Provide a single command (`./support-dump.sh`) that collects system logs, environment diagnostics, and configuration summaries with all passwords and secrets automatically sanitized and redacted.
- [ ] **Immutable Audit Logging**: Record administrative actions (user provisioning, role modifications, data export requests) into a tamper-evident local audit log.

### E. Data Privacy & Zero External Telemetry (GDPR / KVKK)
- [ ] **Zero Unsanctioned Outbound Traffic**: Strictly disable all external analytics, telemetry pings, remote font downloads, and external CDN dependencies in customer environments.
- [ ] **At-Rest Encryption**: Support encryption-at-rest for customer databases and backups, providing scripts for compliance-driven data retention and destruction.

---

## 2. Exit Gate (Field Gate: Customer On-Premises)

An enterprise customer release package cannot be delivered until **all** of the following criteria are satisfied:
1. All Customer On-Premises checklist items are completed in `GOLIVE.md`.
2. Installation successfully executed in a completely air-gapped virtual machine with zero outbound internet connectivity.
3. The pre-flight script verified to block installation cleanly on hosts with insufficient hardware resources.
4. Network traffic inspection (via tcpdump or Wireshark) confirms zero unexpected outbound telemetry, DNS queries, or external asset calls.

---

## 3. Rationale

| Action Item | Why It Is Mandatory |
|:---|:---|
| Air-Gapped Packaging | Financial, defense, and healthcare institutions operate strictly isolated networks. Installers that attempt runtime `npm install` or image pulls fail immediately. |
| Corporate Proxy & Custom CA | Enterprise corporate proxies perform SSL inspection. If the application cannot accept custom internal Root CAs, all TLS calls throw `CERTIFICATE_VERIFY_FAILED`. |
| Sanitized Support Dumps | Remote SSH access into customer environments is typically forbidden. Sanitized diagnostic bundles provide the only viable mechanism for troubleshooting production issues. |
| Zero External Telemetry | Inadvertent calls to external analytics or foreign CDNs from enterprise environments constitute severe compliance violations under GDPR, HIPAA, and KVKK. |

---

## 4. Common Pitfalls

- ❌ **Hidden CDN Dependencies**: Loading fonts (`fonts.googleapis.com`) or icons from public CDNs, causing user interfaces to break inside air-gapped environments.
- ❌ **Dumping Cleartext Passwords in Support Bundles**: Including raw environment files or database credentials in diagnostic logs sent back to vendor support teams.
- ❌ **Hardcoding Hostnames or IPs**: Embedding `localhost` or fixed IP assumptions into code rather than supporting configurable customer hostnames and domains.
- ❌ **Skipping Pre-Flight Checks**: Attempting installation on underspecified customer hosts, resulting in corrupted databases mid-setup.
