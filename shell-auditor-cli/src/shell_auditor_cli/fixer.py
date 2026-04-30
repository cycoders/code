from pathlib import Path
from typing import List

import typer

from .types import Issue


def apply_fixes(path: Path, issues: List[Issue]) -> int:
    """Apply safe fixes (only PERF001 for now). Returns count applied."""
    safe_issues = [i for i in issues if i.rule_id == "PERF001" and i.fix]
    if not safe_issues:
        typer.echo("No safe fixes available.")
        return 0

    text = path.read_text(encoding="utf-8")
    lines = text.splitlines(keepends=True)
    fixes_applied = 0

    for issue in safe_issues:
        line_idx = issue.line - 1
        if line_idx < len(lines):
            old_line = lines[line_idx].rstrip()
            # Verify pattern
            if "cat " in old_line and " | " in old_line:
                lines[line_idx] = issue.fix + "\n"
                fixes_applied += 1
                typer.echo(f"Fixed line {issue.line}: {old_line!r} → {issue.fix!r}")

    if fixes_applied:
        path.write_text("".join(lines), encoding="utf-8")
        typer.echo(f"✅ Applied {fixes_applied} fixes to {path}")
    else:
        typer.echo("No fixes applied.")

    return fixes_applied