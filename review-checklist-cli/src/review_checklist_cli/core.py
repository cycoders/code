from dataclasses import dataclass
from typing import List, Dict, Tuple
import os

from .git_utils import get_changed_files, is_git_repo
from .rules import apply_rules

@dataclass
class ChecklistItem:
    title: str
    description: str
    priority: str  # 'high', 'medium', 'low'
    suggested_command: str | None = None

    def __post_init__(self):
        if self.priority not in ('high', 'medium', 'low'):
            raise ValueError("Priority must be high/medium/low")

def categorize_changes(changes: list[Tuple[str, str]]) -> Dict[str, List[str]]:
    """Categorize paths by type."""
    cats: Dict[str, List[str]] = {
        'python_source': [],
        'tests': [],
        'docker': [],
        'dependencies': [],
        'configs': [],
        'docs': [],
        'security': [],
        'other': [],
    }

    for path, _status in changes:
        name_lower = path.lower()
        ext = os.path.splitext(path)[1].lower()[1:] if '.' in path else ''  # no dot

        if path.endswith(('.py', '.pyx', '.pyi')) and any(skip in name_lower for skip in ('test', 'tests', 'bench')):
            cats['python_source'].append(path)
        elif any(t in name_lower for t in ('test', 'tests/', 'spec', 'bench')) or ext in ('test', 'spec'):
            cats['tests'].append(path)
        elif 'dockerfile' in name_lower or 'dockerignore' in name_lower or ext == 'dockerignore':
            cats['docker'].append(path)
        elif any(lock in name_lower for lock in ('package-lock.json', 'yarn.lock', 'pnpm-lock.yaml', 'poetry.lock', 'pipfile.lock', 'requirements.txt', 'setup.py', 'pyproject.toml')):
            cats['dependencies'].append(path)
        elif ext in ('yaml', 'yml', 'json', 'toml', 'ini', 'env', 'props'):
            cats['configs'].append(path)
        elif ext == 'md' or 'readme' in name_lower:
            cats['docs'].append(path)
        elif any(s in name_lower for s in ('secret', 'key', '.pem', '.crt', 'password')):
            cats['security'].append(path)
        else:
            cats['other'].append(path)

    return {k: v for k, v in cats.items() if v}

def generate_checklist(base: str, head: str, cwd: str = ".") -> List[ChecklistItem]:
    """Full pipeline."""
    if not is_git_repo(cwd):
        raise ValueError("Not a git repository (run in repo root or use --cwd)")

    changes = get_changed_files(base, head, cwd)
    if not changes:
        return []

    categories = categorize_changes(changes)
    items = apply_rules(categories)

    # Global always-items
    globals_ = [
        ChecklistItem("Run pre-commit hooks", "Catch style/security issues early", "medium", "pre-commit run --all-files"),
        ChecklistItem("Full test suite + coverage", "Ensure nothing broke", "high", "pytest --cov"),
        ChecklistItem("Build & deploy dry-run", "Verify CI/CD passes", "medium", "make build || npm run build"),
    ]
    return sorted(items + globals_, key=lambda i: {'high': 0, 'medium': 1, 'low': 2}[i.priority])