import ast
from pathlib import Path
from typing import List

from .types import Issue
from .visitors import DatetimeAuditor


def audit_directory(root: Path) -> List[Issue]:
    """Audit all *.py files in directory recursively."""
    issues: List[Issue] = []
    py_files = list(root.rglob("*.py"))

    for py_file in py_files:
        try:
            source = py_file.read_text(errors="ignore")
            tree = ast.parse(source, filename=str(py_file))
            auditor = DatetimeAuditor(py_file, source)
            auditor.visit(tree)
            issues.extend(auditor.issues)
        except SyntaxError:
            continue  # Skip invalid Python
        except Exception as e:
            print(f"Warning: Failed to audit {py_file}: {e}")
            continue

    return sorted(issues, key=lambda i: (i.file, i.line))