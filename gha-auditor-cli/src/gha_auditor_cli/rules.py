import re
from pathlib import Path
from typing import Callable, Dict, List, Any

from .issue import Issue, Severity


SecretPattern = re.compile(
    r"(?i)(password|secret|key|token|api_key|private_key)\s*[:=]\s*['\"]?([^\s@'\"${}]+)['\"]?",
    re.IGNORECASE,
)


StepsType = List[Dict[str, Any]]
JobsType = Dict[str, Dict[str, Any]]


def get_all_rules() -> List[Callable[[Dict[str, Any], str], List[Issue]]]:
    """Return all audit rules."""
    return [
        rule_unpinned_actions,
        rule_hardcoded_secrets,
        rule_broad_permissions,
        rule_missing_permissions,
        rule_insecure_checkout,
        rule_missing_cache,
    ]


def rule_unpinned_actions(data: Dict[str, Any], file_path: str) -> List[Issue]:
    """Check for unpinned 'uses' actions (security risk)."""
    issues = []
    jobs: JobsType = data.get("jobs", {})
    for job_name, job in jobs.items():
        steps: StepsType = job.get("steps", [])
        for step_idx, step in enumerate(steps):
            uses = step.get("uses")
            if isinstance(uses, str) and "@" not in uses:
                issues.append(
                    Issue(
                        file=file_path,
                        rule="unpinned-action",
                        message=f"Unpinned action '{uses}' in job '{job_name}' step {step_idx}",
                        severity=Severity.MEDIUM,
                    )
                )
            elif isinstance(uses, str) and uses.split("@")[-1] in ("latest", "main", "master"):
                issues.append(
                    Issue(
                        file=file_path,
                        rule="unpinned-action",
                        message=f"Floating ref '{uses}' in job '{job_name}' step {step_idx} (use semver/SHA)",
                        severity=Severity.MEDIUM,
                    )
                )
    return issues


def rule_hardcoded_secrets(data: Dict[str, Any], file_path: str) -> List[Issue]:
    """Detect potential hardcoded secrets in 'run:' steps."""
    issues = []
    jobs: JobsType = data.get("jobs", {})
    for job_name, job in jobs.items():
        steps: StepsType = job.get("steps", [])
        for step_idx, step in enumerate(steps):
            run = step.get("run")
            if isinstance(run, str):
                for match in SecretPattern.finditer(run):
                    if "${{" not in match.group(0):
                        issues.append(
                            Issue(
                                file=file_path,
                                rule="hardcoded-secret",
                                message=f"Potential hardcoded secret in job '{job_name}' step {step_idx}: {match.group(0)}",
                                severity=Severity.HIGH,
                            )
                        )
    return issues


def rule_broad_permissions(data: Dict[str, Any], file_path: str) -> List[Issue]:
    """Flag broad permissions like '*' or excessive writes."""
    issues = []
    # Workflow level
    if (perms := data.get("permissions")):
        if perms.get("*") == "write":
            issues.append(
                Issue(
                    file=file_path,
                    rule="broad-permissions",
                    message="Broad workflow permissions: '*' set to write (scope tightly)",
                    severity=Severity.HIGH,
                )
            )
    # Job level
    jobs: JobsType = data.get("jobs", {})
    for job_name, job in jobs.items():
        if (jperms := job.get("permissions")):  
            write_count = sum(1 for v in jperms.values() if v == "write")
            if write_count > 2:  # heuristic
                issues.append(
                    Issue(
                        file=file_path,
                        rule="broad-permissions",
                        message=f"Job '{job_name}' has {write_count} write permissions (minimize)",
                        severity=Severity.HIGH,
                    )
                )
    return issues


def rule_missing_permissions(data: Dict[str, Any], file_path: str) -> List[Issue]:
    """Warn on missing explicit permissions."""
    issues = []
    if "permissions" not in data:
        issues.append(
            Issue(
                file=file_path,
                rule="missing-permissions",
                message="No explicit workflow permissions (defaults to read-all)",
                severity=Severity.LOW,
            )
        )
    jobs: JobsType = data.get("jobs", {})
    for job_name, job in jobs.items():
        if "permissions" not in job:
            issues.append(
                Issue(
                    file=file_path,
                    rule="missing-permissions",
                    message=f"Job '{job_name}' missing permissions",
                    severity=Severity.LOW,
                )
            )
    return issues


def rule_insecure_checkout(data: Dict[str, Any], file_path: str) -> List[Issue]:
    """Flag insecure checkouts in jobs with write perms."""
    issues = []
    jobs: JobsType = data.get("jobs", {})
    for job_name, job in jobs.items():
        perms = job.get("permissions", {})
        has_write = any(v == "write" for v in perms.values())
        if has_write:
            steps: StepsType = job.get("steps", [])
            has_secure_checkout = False
            for step in steps:
                uses = step.get("uses", "")
                if uses.startswith("actions/checkout@"):
                    with_ = step.get("with", {})
                    if with_.get("token") == "${{ secrets.GITHUB_TOKEN }}":
                        has_secure_checkout = True
                        break
            if not has_secure_checkout:
                issues.append(
                    Issue(
                        file=file_path,
                        rule="insecure-checkout",
                        message=f"Job '{job_name}' has write perms but insecure checkout (add token: ${{ secrets.GITHUB_TOKEN }})",
                        severity=Severity.MEDIUM,
                    )
                )
    return issues


def rule_missing_cache(data: Dict[str, Any], file_path: str) -> List[Issue]:
    """Suggest caching for common setup actions."""
    issues = []
    jobs: JobsType = data.get("jobs", {})
    for job_name, job in jobs.items():
        steps: StepsType = job.get("steps", [])
        has_cache = False
        for step in steps:
            uses = step.get("uses", "")
            if "cache" in step:
                has_cache = True
                break
            if uses.startswith(("actions/setup-node@", "actions/setup-python@")):
                if step.get("with", {}).get("cache"):
                    has_cache = True
        if not has_cache:
            issues.append(
                Issue(
                    file=file_path,
                    rule="missing-cache",
                    message=f"Job '{job_name}' missing caching (add to setup-* actions)",
                    severity=Severity.LOW,
                )
            )
    return issues
