import logging
from pathlib import Path
from typing import List

import yaml
from rich.progress import track

from .issue import Issue, Severity
from .rules import get_all_rules


logger = logging.getLogger(__name__)


def audit_directory(dir_path: Path) -> List[Issue]:
    """Audit all GitHub Actions workflows in the directory."""

    workflows_dir = dir_path / ".github" / "workflows"
    if not workflows_dir.is_dir():
        logger.info("No .github/workflows directory found.")
        return []

    all_issues: List[Issue] = []

    workflow_files = list(workflows_dir.glob("*.yml")) + list(workflows_dir.glob("*.yaml"))
    if not workflow_files:
        logger.info("No workflow files (*.yml/*.yaml) found.")
        return []

    for wf_file in track(workflow_files, description="Auditing workflows..."):
        try:
            issues = _audit_file(wf_file)
            all_issues.extend(issues)
        except Exception as e:
            all_issues.append(
                Issue(
                    file=str(wf_file),
                    rule="parse-error",
                    message=f"Failed to parse: {str(e)}",
                    severity=Severity.HIGH,
                )
            )

    return all_issues


def _audit_file(wf_file: Path) -> List[Issue]:
    with open(wf_file, "r") as f:
        data = yaml.safe_load(f)

    if not isinstance(data, dict):
        raise ValueError("Invalid YAML: root must be object")

    issues: List[Issue] = []
    file_path = str(wf_file)

    for rule in get_all_rules():
        try:
            rule_issues = rule(data, file_path)
            issues.extend(rule_issues)
        except Exception as e:
            logger.warning(f"Rule failed on {file_path}: {e}")

    return issues
