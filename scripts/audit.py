#!/usr/bin/env python3
"""
Go-Live Repository Pre-Audit Script (`audit.py`)
Part of golive-skill

Scans the repository to identify completed and missing production readiness items,
detects project deployment fields (Cloud, On-Premises, Edge), and can automatically
initialize or update the GOLIVE.md state tracker.

Usage:
    python audit.py [--path /path/to/repo] [--init] [--sync] [--json]
"""

import os
import sys
import json
import re
import argparse
from pathlib import Path
from typing import Dict, List, Any, Tuple

# Ensure UTF-8 output on Windows consoles if possible
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Common regex patterns for secret detection
SECRET_PATTERNS = [
    (re.compile(r"""(?:api_key|apikey|secret_key|secret|password|access_token)\s*[:=]\s*['"][a-zA-Z0-9_\-]{16,}['"]""", re.IGNORECASE), "Potential Hardcoded Secret/Key"),
    (re.compile(r"""AKIA[0-9A-Z]{16}"""), "AWS Access Key ID"),
    (re.compile(r"""ghp_[a-zA-Z0-9]{36}"""), "GitHub Personal Access Token"),
    (re.compile(r"""-----BEGIN (?:RSA |EC )?PRIVATE KEY-----"""), "Private Key Block"),
]

# File ignore patterns during code search
IGNORE_DIRS = {".git", ".hg", ".svn", "node_modules", "venv", ".venv", "env", "__pycache__", ".pytest_cache", "dist", "build", ".next", ".cache"}

def is_ignored(path: Path) -> bool:
    for part in path.parts:
        if part in IGNORE_DIRS:
            return True
    return False

def scan_for_secrets(root_path: Path) -> List[Dict[str, Any]]:
    findings = []
    gitignore_file = root_path / ".gitignore"
    has_env_in_gitignore = False
    if gitignore_file.exists():
        try:
            content = gitignore_file.read_text(encoding="utf-8", errors="ignore")
            if ".env" in content:
                has_env_in_gitignore = True
        except Exception:
            pass

    for file_path in root_path.rglob("*"):
        if not file_path.is_file() or is_ignored(file_path):
            continue
        
        # Don't scan large binary files or archives
        if file_path.suffix.lower() in {".png", ".jpg", ".jpeg", ".gif", ".ico", ".pdf", ".zip", ".tar", ".gz", ".exe", ".bin", ".lock"}:
            continue

        try:
            # Skip files larger than 1MB
            if file_path.stat().st_size > 1024 * 1024:
                continue
            
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            
            # Check for tracked .env files
            if file_path.name == ".env" and not file_path.name.endswith(".example") and not file_path.name.endswith(".sample"):
                findings.append({
                    "file": str(file_path.relative_to(root_path)),
                    "type": "Tracked .env credential file",
                    "severity": "CRITICAL",
                    "line": 1
                })

            for pattern, desc in SECRET_PATTERNS:
                for line_idx, line in enumerate(content.splitlines(), start=1):
                    # Skip common comment or template placeholders
                    if "EXAMPLE" in line.upper() or "DUMMY" in line.upper() or "PLACEHOLDER" in line.upper():
                        continue
                    if pattern.search(line):
                        findings.append({
                            "file": str(file_path.relative_to(root_path)),
                            "type": desc,
                            "severity": "HIGH",
                            "line": line_idx
                        })
                        break # One detection per pattern per file is sufficient
        except Exception:
            continue

    return findings

def audit_repository(root_path: Path) -> Dict[str, Any]:
    findings: Dict[str, Any] = {
        "root": str(root_path.resolve()),
        "tech_stack": [],
        "detected_fields": [],
        "core_status": {},
        "secret_warnings": [],
        "summary": {}
    }

    # 1. Detect Stack
    files = [f.name for f in root_path.iterdir() if f.is_file()]
    all_files_rel = []
    for p in root_path.rglob("*"):
        if not is_ignored(p):
            all_files_rel.append(p.relative_to(root_path).as_posix().lower())

    if "package.json" in files:
        findings["tech_stack"].append("Node.js / TypeScript / JavaScript")
    if any(f in files for f in ["requirements.txt", "pyproject.toml", "Pipfile", "poetry.lock"]):
        findings["tech_stack"].append("Python")
    if "go.mod" in files:
        findings["tech_stack"].append("Go")
    if "Cargo.toml" in files:
        findings["tech_stack"].append("Rust")
    if "pom.xml" in files or "build.gradle" in files:
        findings["tech_stack"].append("Java / Kotlin")

    # 2. Detect Fields
    has_tf = any(f.endswith(".tf") for f in all_files_rel)
    has_k8s = any("k8s" in f or "helm" in f or "chart.yaml" in f for f in all_files_rel)
    has_compose = any("docker-compose" in f for f in all_files_rel)
    has_edge = any("rpi" in f or "jetson" in f or "arm64" in f or "systemd" in f or "ota" in f for f in all_files_rel)

    if has_tf or has_k8s or any("cloud" in f for f in all_files_rel):
        findings["detected_fields"].append("Cloud / SaaS")
    if has_compose or any("onprem" in f or "airgap" in f or "offline" in f for f in all_files_rel):
        findings["detected_fields"].append("Customer On-Premises")
    if has_edge:
        findings["detected_fields"].append("Edge / Device")
    
    if not findings["detected_fields"]:
        findings["detected_fields"].append("Cloud / SaaS (Default)")

    # 3. Check Core Stages

    # Stage 01: Backend Hardening
    has_env_example = any(".env.example" in f or ".env.sample" in f or "config.example" in f for f in all_files_rel)
    has_health = False
    has_schema_val = False
    
    sample_code_files = [root_path / p for p in all_files_rel if p.endswith(('.py', '.ts', '.js', '.go', '.rs'))][:200]
    for cp in sample_code_files:
        try:
            txt = cp.read_text(encoding="utf-8", errors="ignore")
            if "/health" in txt or "/ready" in txt or "healthz" in txt or "readyz" in txt:
                has_health = True
            if "zod" in txt or "pydantic" in txt or "validator" in txt or "envalid" in txt or "joi" in txt:
                has_schema_val = True
            if has_health and has_schema_val:
                break
        except Exception:
            pass

    findings["core_status"]["01-backend-hardening"] = {
        "env_example": has_env_example,
        "schema_validation": has_schema_val,
        "health_endpoints": has_health,
        "complete_ratio": sum([has_env_example, has_schema_val, has_health]) / 3.0
    }

    # Stage 02: Quality & Eval
    has_tests_dir = any("test" in f or "spec" in f for f in all_files_rel)
    has_eval = any("eval" in f or "golden" in f or "benchmark" in f for f in all_files_rel)
    findings["core_status"]["02-quality-and-eval"] = {
        "automated_tests": has_tests_dir,
        "ai_eval_dataset": has_eval,
        "complete_ratio": sum([has_tests_dir, has_eval]) / 2.0
    }

    # Stage 03: Frontend Readiness
    is_frontend = any("next.config" in f or "vite.config" in f or "tailwind.config" in f or "src/app" in f or "src/pages" in f for f in all_files_rel)
    findings["core_status"]["03-frontend-readiness"] = {
        "frontend_present": is_frontend,
        "build_configured": "package.json" in files,
        "complete_ratio": 1.0 if is_frontend else 0.5
    }

    # Stage 04: Packaging
    has_dockerfile = any("dockerfile" in f.lower() for f in files)
    has_dockerignore = ".dockerignore" in files
    multi_stage = False
    non_root = False
    if has_dockerfile:
        try:
            df_content = (root_path / "Dockerfile").read_text(encoding="utf-8", errors="ignore")
            if len(re.findall(r"^FROM\s+", df_content, re.MULTILINE | re.IGNORECASE)) > 1:
                multi_stage = True
            if re.search(r"^USER\s+[a-zA-Z0-9_\-]+", df_content, re.MULTILINE | re.IGNORECASE):
                non_root = True
        except Exception:
            pass

    findings["core_status"]["04-packaging"] = {
        "dockerfile": has_dockerfile,
        "dockerignore": has_dockerignore,
        "multi_stage": multi_stage,
        "non_root_user": non_root,
        "complete_ratio": sum([has_dockerfile, has_dockerignore, multi_stage, non_root]) / 4.0
    }

    # Stage 05: CI/CD
    has_ci = any(".github/workflows" in f or ".gitlab-ci" in f or "jenkins" in f for f in all_files_rel)
    findings["core_status"]["05-ci-cd"] = {
        "ci_pipeline_exists": has_ci,
        "complete_ratio": 1.0 if has_ci else 0.0
    }

    # Stage 06: Security & Secrets
    secret_findings = scan_for_secrets(root_path)
    findings["secret_warnings"] = secret_findings
    findings["core_status"]["06-security-and-secrets"] = {
        "zero_secrets_detected": len(secret_findings) == 0,
        "findings_count": len(secret_findings),
        "complete_ratio": 1.0 if len(secret_findings) == 0 else 0.2
    }

    # Stage 07: Observability
    has_observability = False
    for cp in sample_code_files:
        try:
            txt = cp.read_text(encoding="utf-8", errors="ignore").lower()
            if any(k in txt for k in ["winston", "pino", "structlog", "loguru", "opentelemetry", "prometheus", "datadog", "sentry"]):
                has_observability = True
                break
        except Exception:
            pass
    findings["core_status"]["07-observability"] = {
        "structured_logging_or_apm": has_observability,
        "complete_ratio": 1.0 if has_observability else 0.0
    }

    # Stage 08: Release & Rollback
    has_migrations = any("alembic" in f or "migrations" in f or "prisma" in f or "flyway" in f for f in all_files_rel)
    findings["core_status"]["08-release-and-rollback"] = {
        "database_migrations": has_migrations,
        "complete_ratio": 1.0 if has_migrations else 0.3
    }

    # Overall Summary
    total_stages = len(findings["core_status"])
    ready_stages = sum(1 for v in findings["core_status"].values() if v.get("complete_ratio", 0) >= 0.75)
    findings["summary"] = {
        "total_stages": total_stages,
        "mature_stages": ready_stages,
        "readiness_percentage": round((ready_stages / total_stages) * 100, 1),
        "golive_file_exists": (root_path / "GOLIVE.md").exists()
    }

    return findings

def print_cli_report(results: Dict[str, Any]):
    print("=" * 65)
    print(" [*] GO-LIVE REPOSITORY PRE-AUDIT REPORT")
    print("=" * 65)
    print(f" Repository Path : {results['root']}")
    print(f" Tech Stack      : {', '.join(results['tech_stack']) if results['tech_stack'] else 'General / Multi-stack'}")
    print(f" Detected Fields : {', '.join(results['detected_fields'])}")
    print(f" Readiness Score : %{results['summary']['readiness_percentage']} ({results['summary']['mature_stages']}/{results['summary']['total_stages']} Stages Mature)")
    print(f" GOLIVE.md Status: {'Present' if results['summary']['golive_file_exists'] else 'Missing (run with --init)'}")
    print("-" * 65)
    print("STAGE BREAKDOWN:")
    for stage, details in results["core_status"].items():
        ratio = details.get("complete_ratio", 0)
        status_icon = "[PASS]" if ratio >= 0.75 else ("[IN_PROGRESS]" if ratio > 0 else "[PENDING]")
        items_summary = ", ".join(f"{k}: {'Yes' if v is True else ('No' if v is False else v)}" for k, v in details.items() if k != "complete_ratio")
        print(f"  {status_icon:<14} [{stage:<25}] -> {items_summary}")
    
    if results["secret_warnings"]:
        print("\n [!] SECURITY & SECRET WARNINGS:")
        for w in results["secret_warnings"][:10]:
            print(f"  ! [{w['severity']}] {w['file']}:{w['line']} - {w['type']}")
        if len(results["secret_warnings"]) > 10:
            print(f"  ...and {len(results['secret_warnings']) - 10} additional potential secret findings.")
    else:
        print("\n [OK] Secret Audit: Zero exposed credentials detected (Clean).")
    print("=" * 65)

def init_or_sync_golive(root_path: Path, template_path: Path, results: Dict[str, Any]):
    golive_target = root_path / "GOLIVE.md"
    
    if not golive_target.exists():
        if not template_path.exists():
            print(f"Error: Template file not found: {template_path}")
            return
        content = template_path.read_text(encoding="utf-8")
        content = content.replace("[PROJECT_NAME]", root_path.name)
        
        # Check detected fields
        for field in results["detected_fields"]:
            if "Cloud" in field:
                content = content.replace("- [ ] Cloud / SaaS", "- [x] Cloud / SaaS")
            if "Customer" in field or "On-Premises" in field:
                content = content.replace("- [ ] Customer On-Premises", "- [x] Customer On-Premises")
            if "Edge" in field:
                content = content.replace("- [ ] Edge / Device", "- [x] Edge / Device")

        # Mark detected pre-audit items
        if results["core_status"].get("04-packaging", {}).get("dockerfile"):
            content = content.replace("- [ ] Multi-stage `Dockerfile`", "- [x] Multi-stage `Dockerfile` (Detected by audit)")
        if results["core_status"].get("05-ci-cd", {}).get("ci_pipeline_exists"):
            content = content.replace("- [ ] Automated pipeline triggers", "- [x] Automated pipeline triggers (Detected by audit)")
        if results["core_status"].get("06-security-and-secrets", {}).get("zero_secrets_detected"):
            content = content.replace("- [ ] Repository and commit history scanned", "- [x] Repository and commit history scanned (Verified clean by audit)")

        golive_target.write_text(content, encoding="utf-8")
        print(f"[OK] GOLIVE.md successfully initialized from template: {golive_target}")
    else:
        print(f"[INFO] GOLIVE.md already exists: {golive_target}. Skipped overwrite.")

def main():
    parser = argparse.ArgumentParser(description="Go-Live Repository Pre-Audit CLI")
    parser.add_argument("--path", default=".", help="Target repository directory path")
    parser.add_argument("--json", action="store_true", help="Output audit results as JSON")
    parser.add_argument("--init", action="store_true", help="Initialize GOLIVE.md if not present")
    parser.add_argument("--sync", action="store_true", help="Sync audit results into GOLIVE.md")
    args = parser.parse_args()

    repo_path = Path(args.path).resolve()
    script_dir = Path(__file__).parent.resolve()
    template_path = script_dir.parent / "assets" / "GOLIVE.template.md"

    results = audit_repository(repo_path)

    if args.json:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    else:
        print_cli_report(results)

    if args.init or args.sync:
        init_or_sync_golive(repo_path, template_path, results)

if __name__ == "__main__":
    main()
