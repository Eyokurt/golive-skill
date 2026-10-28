# Stage 06: Security & Secret Management (Security & Secrets)

> **Objective**: Safeguard application credentials, encryption keys, and customer data; eliminate unauthorized access vectors, credential stuffing risks, and standard web vulnerabilities before reaching production.

---

## 1. Action Items

### A. Zero Secrets in Code
- [ ] **Repository Credential Audit**: Scan the entire codebase, branch history, and pull requests using tools like `gitleaks` or `trufflehog`; enforce 100% clean status with zero exposed keys or `.pem` certificates.
- [ ] **Centralized Secret Stores**: Production credentials must not reside in plain text `.env` files. Inject them at runtime from dedicated vaults (AWS Secrets Manager, HashiCorp Vault, GCP Secret Manager).
- [ ] **Key Rotation Readiness**: Document and test rotation procedures for database credentials and external API tokens to ensure seamless rotation without service downtime.

### B. Supply Chain & Dependency Auditing
- [ ] **Vulnerability Auditing**: Audit project dependencies (`npm audit`, `pip-audit`, `cargo audit`, `trivy fs .`); remediate or isolate any libraries with `CRITICAL` or `HIGH` severity vulnerabilities.
- [ ] **Dependency Pinning**: Pin all third-party dependencies to exact, deterministic version numbers.

### C. Network, CORS & HTTP Security Headers
- [ ] **Strict CORS Policies**: `Access-Control-Allow-Origin: *` is strictly prohibited. Whitelist only explicitly verified client domains.
- [ ] **Security Headers**:
  - `Content-Security-Policy (CSP)`: Restrict executable script and resource origins to protect against cross-site scripting (XSS).
  - `Strict-Transport-Security (HSTS)`: Enforce HTTPS via `max-age=31536000; includeSubDomains; preload`.
  - `X-Content-Type-Options: nosniff`: Prevent MIME-type sniffing exploits.
  - `X-Frame-Options: DENY`: Defend against clickjacking attacks.

### D. Rate Limiting & Abuse Prevention
- [ ] **Authentication Rate Limiting**: Limit sensitive endpoints (login, password reset, registration) to a maximum of 5-10 requests per minute per IP.
- [ ] **DDoS & Web Application Firewalls (WAF)**: Enable bot mitigation, geographic rules, and anomaly detection via Cloudflare, AWS WAF, or reverse proxy layers.
- [ ] **Input Sanitization & Parameterization**: Defend against SQL Injection, NoSQL Injection, and SSRF attacks using parameterized ORM queries and strict input schema validation.

---

## 2. Exit Gate (Gate 06)

Stage 07 cannot commence until **all** of the following criteria are satisfied:
1. All Stage 06 checklist items are completed in `GOLIVE.md`.
2. Static secret scans (`gitleaks`) return zero exposed credentials across repository history.
3. Dependency vulnerability auditing reports zero `CRITICAL` and zero `HIGH` severity issues.
4. Validating live response headers (`curl -I <api_url>`) confirms active HSTS, X-Frame-Options, and restricted CORS origins.

---

## 3. Rationale

| Action Item | Why It Is Mandatory |
|:---|:---|
| Git Secret Scanning | Database credentials committed to public or shared repositories are discovered and exploited by automated scrapers within seconds. |
| Wildcard CORS Ban | Permissive CORS allows malicious third-party websites to forge requests using users' active browser sessions. |
| Login Rate Limiting | Without rate limiting, automated attackers can execute high-speed credential stuffing against user accounts. |
| HSTS & Security Headers | Provides browser-level defenses against Man-in-the-Middle (MitM) and clickjacking attacks before requests reach application code. |

---

## 4. Common Pitfalls

- ❌ **Deleting Secrets with `git rm`**: Removing the file without rewriting git history leaves credentials permanently readable in historical commits.
- ❌ **Opening CORS for "Convenience"**: Pairing `Access-Control-Allow-Origin: *` with `Allow-Credentials: true`, exposing internal APIs to cross-origin data theft.
- ❌ **Logging Cleartext Passwords**: Recording un-sanitized user login request bodies directly into server logs.
- ❌ **Rolling Custom Cryptography**: Implementing ad-hoc hashing routines instead of industry-standard algorithms (bcrypt, Argon2, PBKDF2).
