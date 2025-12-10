import re
from typing import Tuple, List

def validate_commit(msg: str) -> Tuple[bool, List[str]]:
    """Validate conventional commit format."""
    issues: List[str] = []
    lines = msg.strip().splitlines()
    if not lines:
        issues.append("Empty message")
        return False, issues

    subject = lines[0].strip()
    if len(subject) > 72:
        issues.append("Subject >72 chars")
    if len(msg) > 10000:
        issues.append("Body too long")

    # Conventional format: type(scope)!?: subject
    pattern = re.compile(
        r"^(feat|fix|docs|style|refactor|perf|test|build|ci|chore|revert)"
        r"(?:\([a-z0-9\-_]+\))?"  # optional scope
        r"(?:!)?: "  # optional !breaking
        r"(.{1,72})$"
    )
    match = pattern.match(subject)
    if not match:
        issues.append(
            "Invalid format: 'type[(scope)] [!]: subject' (subject <=72 chars)"
        )

    # Body lines <=100
    for i, line in enumerate(lines[1:], 2):
        if len(line.strip()) > 100:
            issues.append(f"Line {i} >100 chars")

    return len(issues) == 0, issues
