from typing import List, Dict
from .core import ChecklistItem

def apply_rules(categories: Dict[str, List[str]]) -> List[ChecklistItem]:
    """Apply category-specific rules."""
    items: List[ChecklistItem] = []

    # Python source
    py_src = categories.get('python_source', [])
    if py_src:
        num_py = len(py_src)
        items.extend([
            ChecklistItem(
                "Run type checker",
                f"Check {num_py} Python files for type errors",
                "high",
                "mypy " + " ".join(py_src) if num_py < 5 else "mypy src/",
            ),
            ChecklistItem(
                "Lint Python code",
                "Enforce style & best practices",
                "medium",
                "ruff check " + " ".join(py_src),
            ),
            ChecklistItem(
                "Review imports & deps",
                "Check for new/unused imports",
                "medium",
            ),
        ])

    # Tests
    tests = categories.get('tests', [])
    py_src = bool(categories.get('python_source'))
    if tests:
        items.append(
            ChecklistItem(
                "Run changed tests",
                f"Execute {len(tests)} test files",
                "high",
                "pytest " + " ".join(tests),
            )
        )
    elif py_src:
        items.append(
            ChecklistItem(
                "Add tests for changes",
                "No tests changed; ensure src changes covered",
                "high",
            )
        )

    # Dependencies
    if categories.get('dependencies'):
        items.extend([
            ChecklistItem(
                "Verify lockfile reproducibility",
                "Test exact dep resolution",
                "high",
                "pip install -r requirements.txt --dry-run --report -",
            ),
            ChecklistItem(
                "Scan new deps for vulns",
                "Use osv-scanner or npm audit",
                "high",
                "osv-scanner || pip-audit || npm audit",
            ),
            ChecklistItem(
                "Review dep upgrades",
                "Check changelogs for breaking changes",
                "medium",
            ),
        ])

    # Docker
    if categories.get('docker'):
        items.extend([
            ChecklistItem("Build Docker image", "Verify no-cache build", "high", "docker build --no-cache ."),
            ChecklistItem("Scan for vulnerabilities", "Use trivy/docker scout", "high", "trivy image ."),
            ChecklistItem("Optimize layers", "Check for large/unnecessary layers", "medium"),
        ])

    # Configs
    if categories.get('configs'):
        items.extend([
            ChecklistItem("Validate configs", "Check syntax (yamllint, json)" , "medium", "yamllint ."),
            ChecklistItem("Diff across envs", "Ensure prod/staging align", "low"),
        ])

    # Security
    if categories.get('security'):
        items.extend([
            ChecklistItem("Secrets scan", "Hunt for committed creds", "high", "git-secrets-scanner --scan ."),
            ChecklistItem("Review certs/keys", "Expiry/permissions", "high"),
        ])

    # Docs
    if categories.get('docs'):
        items.append(
            ChecklistItem("Check links", "No broken links in docs", "low", "link-auditor README.md"),
        )

    # Other
    if categories.get('other'):
        items.append(
            ChecklistItem("Manual review", f"{len(categories['other'])} uncategorized files", "low"),
        )

    return items