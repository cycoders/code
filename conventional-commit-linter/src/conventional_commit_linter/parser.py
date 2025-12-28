import re
from typing import Any, Dict, Optional


def parse_header(header: str) -> Dict[str, Any]:
    """
    Parse conventional commit header.

    >>> parse_header('feat(ui)!: subject')
    {'type': 'feat', 'scope': 'ui', 'breaking': True, 'subject': 'subject'}

    Raises:
        ValueError: Invalid header format.
    """
    pattern = r"^([a-z]+)(?:\(([^)\s]+)\))?(!)?:\s*(.+)$"
    match = re.match(pattern, header.strip(), re.IGNORECASE)
    if not match:
        raise ValueError(f"Invalid commit header: {header!r}")

    typ, scope, breaking, subject = match.groups()
    return {
        "type": typ.lower(),
        "scope": scope.lower() if scope else None,
        "breaking": bool(breaking),
        "subject": subject.strip(),
    }


def parse_commit_message(message: str) -> Dict[str, Any]:
    """
    Full parser for commit message.

    Splits header/body/footer, detects BREAKING CHANGE.
    """
    if not message.strip():
        raise ValueError("Commit message cannot be empty")

    lines = [line.rstrip() for line in message.strip().splitlines()]
    header_data = parse_header(lines[0])

    # Body: non-empty lines after header until blank
    body_lines = []
    i = 1
    while i < len(lines) and lines[i].strip():
        body_lines.append(lines[i])
        i += 1

    # Skip blanks
    while i < len(lines) and not lines[i].strip():
        i += 1

    # Footer: KEY: value
    footer: Dict[str, str] = {}
    for line in lines[i:]:
        stripped = line.strip()
        if ":" in stripped:
            key, value = stripped.split(":", 1)
            footer[key.strip().upper()] = value.strip()

    parsed = {
        **header_data,
        "body": "\n".join(body_lines),
        "footer": footer,
    }

    # Breaking change
    if footer.get("BREAKING CHANGE") or header_data["breaking"]:
        parsed["breaking"] = True

    return parsed
