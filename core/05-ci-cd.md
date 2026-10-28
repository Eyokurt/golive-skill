# Stage 05: Continuous Integration & Deployment (CI/CD Pipeline)

> **Objective**: Eliminate human error from building, testing, auditing, and deploying software by establishing a fully automated, reproducible, gate-driven pipeline with explicit environment separation and manual approval controls for production.

---

## 1. Action Items

### A. Pipeline Stages & Automated Gates
- [ ] **Triggers**: Automated pipelines must run on all Pull Requests and merges to primary branches (`main`/`master`).
- [ ] **Sequential Stages**:
  1. *Lint & Typecheck*: Static analysis and type verification (`tsc --noEmit`, `ruff`, `flake8`, `biome`).
  2. *Security SAST & Secret Scan*: Code analysis and secret detection (`gitleaks`, `semgrep`).
  3. *Automated Testing*: Unit and integration test execution with coverage checks.
  4. *Docker Build & Vulnerability Scan*: Container build and CVE scanning (Trivy).
  5. *Artifact Publishing*: Push verified container images to private registries with immutable SHA tags.
- [ ] **Fail-Fast Enforcement**: If any step fails (even formatting or a single test), the pipeline must abort immediately and block subsequent actions.

### B. Environment Isolation & Secret Security
- [ ] **Environment Separation**: Maintain distinct variable scopes and deployment credentials across `Development`, `Staging`, and `Production` environments.
- [ ] **Short-Lived Cloud Credentials (OIDC)**: Connect CI/CD runners (GitHub Actions, GitLab CI) to cloud providers (AWS, GCP, Azure) via OpenID Connect (OIDC) and IAM role assumption rather than static, long-lived access keys.
- [ ] **Secret Masking**: Verify that all CI secrets and tokens are automatically masked in build logs.

### C. Branch Protection & Manual Approval Gates
- [ ] **Main Branch Protection Rules**:
  - Direct pushes to `main` (`git push origin main`) must be strictly disabled.
  - Require at least one approved peer review from senior maintainers.
  - Require all automated status checks to pass before merging.
- [ ] **Manual Production Deployment Gate**:
  - Deployments to staging may proceed automatically, but production releases must require explicit manual approval from authorized engineers.

---

## 2. Exit Gate (Gate 05)

Stage 06 cannot commence until **all** of the following criteria are satisfied:
1. All Stage 05 checklist items are completed in `GOLIVE.md`.
2. A verified PR demonstrates clean execution across all stages (Lint -> Test -> Build -> Vulnerability Scan).
3. Branch protection rules verified active via repository settings.
4. Production deployment pipeline verified to enforce manual gate approval.

---

## 3. Rationale

| Action Item | Why It Is Mandatory |
|:---|:---|
| OIDC Authentication | Static AWS access keys leaked from CI configurations allow attackers to compromise cloud infrastructure without expiration. |
| Branch Protection | Prevents developers from accidentally pushing broken or untested local code straight to production branches. |
| Manual Production Gate | Prevents inadvertent deployments during off-hours, holidays, or when on-call teams are unavailable to respond to incidents. |
| Automated Secret Scanning | Catches mistakenly committed API keys and credentials the moment code enters the pipeline. |

---

## 4. Common Pitfalls

- ❌ **Allowing `--force` Pushes on Primary Branches**: Permitting developers to overwrite commit history and bypass audit trails.
- ❌ **Bypassing Failing Tests**: Adding `if: always()` or skipping tests in CI to force deployments through.
- ❌ **Printing Secrets to Build Logs**: Running verbose debug scripts (`echo $SECRET`) that expose credentials in publicly visible build outputs.
- ❌ **Deploying Directly from Local Workstations**: Deploying to production without going through CI pipelines, eliminating reproducibility and accountability.
