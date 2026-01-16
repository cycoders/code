import json
import re
from pathlib import Path
from typing import List, Dict, Any

PII_PATTERNS = [
    r'\b(?:[0-9]{{1,3}}\\.){{3}}[0-9]{{1,3}}\b',  # IPv4
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\\.[A-Z|a-z]{{2,}}\b',  # email
    r'\b\d{{4}}[-/]\d{{2}}[-/]\d{{2}}\b',  # YYYY-MM-DD
    r'/dev/null',  # placeholder
]


def redact_chunk(chunk: str) -> str:
    for pattern in PII_PATTERNS:
        chunk = re.sub(pattern, '[REDACTED]', chunk, flags=re.IGNORECASE | re.MULTILINE)
    return chunk


def redact_session(input_path: Path, output_path: Path) -> None:
    """Redact PII in stdout chunks."""
    with open(input_path, encoding="utf-8") as f:
        data: List[Dict[str, Any]] = json.load(f)

    for event in data[1:]:
        if 'stdout' in event:
            event['stdout'] = redact_chunk(event['stdout'])

    output_path.write_text(json.dumps(data, indent=2))
