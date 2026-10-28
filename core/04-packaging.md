# Stage 04: Packaging & Containerization (Packaging)

> **Objective**: Package the application into an immutable, minimal, reproducible, and secure container image or distribution bundle that runs consistently across development, staging, and production environments.

---

## 1. Action Items

### A. Multi-Stage Builds
- [ ] **Build vs. Runtime Separation**: Use at least two distinct stages in the `Dockerfile` (e.g., `builder` and `runner`).
- [ ] **Minimal Runtime Footprint**: Compilers, SDKs, devDependencies, git, and package managers must not bleed into the final production image.
- [ ] **Minimal Base Images**: Use minimal, audited official base images (e.g., `alpine`, `distroless`, `slim`).

### B. Security & Least Privilege
- [ ] **Non-Root Execution**: Create a dedicated system user and group (`USER appuser:appgroup` or `USER 10001:10001`). Never execute containers as root (`UID 0`).
- [ ] **Restricted File Permissions**: Set application directories to read-only where possible (`chmod -R 550`), strictly scoping writable permissions to isolated temporary directories (`/tmp`).

### C. Dependency Locking & Reproducibility
- [ ] **Pinned Lockfiles**: Install dependencies strictly from verified lockfiles (`package-lock.json`, `pnpm-lock.yaml`, `poetry.lock`, `uv.lock`, `go.sum`, `Cargo.lock`) using deterministic install commands (`npm ci`, `poetry install --no-dev`, `uv sync --frozen`).
- [ ] **Immutable Tagging**: The `:latest` tag is strictly forbidden for production deployments. Tag images with semantic versioning and git commit SHAs (e.g., `myapp:v1.2.0-sha1a2b3c`); record image digest hashes (SHA256).

### D. Asset Hygiene & Vulnerability Scanning
- [ ] **Exhaustive `.dockerignore`**: Ensure the `.dockerignore` file excludes:
  - `.git`, `.github`
  - `.env`, `.env.*` (local credentials)
  - `node_modules`, `venv`, `__pycache__`, `.pytest_cache`
  - `tests/`, `docs/`, `docker-compose*.yml`
- [ ] **Vulnerability Auditing**: Scan container images with tools such as Trivy, Grype, or Docker Scout; enforce zero `CRITICAL` severity CVEs.

---

## 2. Exit Gate (Gate 04)

Stage 05 cannot commence until **all** of the following criteria are satisfied:
1. All Stage 04 checklist items are completed in `GOLIVE.md`.
2. Running `docker run --rm <image_tag> whoami` outputs an unprivileged non-root user.
3. Container vulnerability scanner reports zero `CRITICAL` severity CVEs.
4. Image sizes satisfy architectural constraints (e.g., Node.js < 180MB, Python FastAPI < 150MB, Go binary < 40MB).

---

## 3. Rationale

| Action Item | Why It Is Mandatory |
|:---|:---|
| Multi-Stage Builds | Reduces image footprint from 1.5GB to 80MB. Smaller images reduce network transfer times, speed up cold starts, and minimize attack surfaces. |
| Non-Root User | In the event of a container breakout exploit, the attacker cannot easily obtain root privileges on the underlying host node. |
| Locked Dependencies | Open-ended installs introduce breaking changes when upstream maintainers release patch versions, leading to unreproducible builds. |
| Comprehensive `.dockerignore` | Prevents accidental baking of local `.env` files into public or shared container registries. |

---

## 4. Common Pitfalls

- ❌ **Running as `root`**: Leaving container defaults unconfigured and executing processes with root capabilities.
- ❌ **Baking Secrets into Image Layers**: Copying credentials during intermediate stages where they remain recoverable in image history.
- ❌ **Deploying with `:latest`**: Obscuring exactly which commit is deployed and causing rollback procedures to fail.
- ❌ **Invalidating Docker Build Cache**: Copying application source code before dependency definitions (`package.json`), forcing unnecessary rebuilds of unchanged libraries.
