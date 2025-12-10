import json
import re
from typing import Dict, Any, Optional, List
import pendulum

# Default patterns for common log formats
DEFAULT_PATTERNS = [
    r'^(?P<timestamp>\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d{3})?(?:Z|[+-]\d{2}:\d{2})?)\s+(?P<level>\w+)\s+(?P<service>\w+):\s+(?P<message>.*)',
    r'\[(?P<timestamp>\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]\s+(?P<level>\w+):\s+(?P<message>.*)',
    r'(?P<timestamp>\d{4}/\d{2}/\d{2}\s+\d{2}:\d{2}:\d{2})\s+(?P<level>\w+)\s+(?P<message>.*)',
]

JSON_DETECTOR = re.compile(r'^\s*\{')


def parse_line(line: str, patterns: Optional[List[str]] = None) -> Optional[Dict[str, Any]]:
    """
    Parse a log line to structured dict.

    Supports:
    - JSON lines
    - Regex patterns (timestamp, level, etc.)
    - Fallback to raw
    """
    line = line.strip()
    if not line:
        return None

    # JSON first
    if JSON_DETECTOR.match(line):
        try:
            data = json.loads(line)
            data.setdefault("parsed_at", pendulum.now("UTC"))
            return data
        except json.JSONDecodeError:
            pass

    # Regex patterns
    pats = patterns or DEFAULT_PATTERNS
    for pat in pats:
        match = re.match(pat, line)
        if match:
            data = match.groupdict()
            if "timestamp" in data:
                ts_str = data["timestamp"]
                try:
                    data["timestamp"] = pendulum.parse(ts_str)
                except ValueError:
                    data["timestamp"] = ts_str  # Keep string
            data["raw_line"] = line
            data["parsed_at"] = pendulum.now("UTC")
            return data

    # Fallback
    return {
        "raw_line": line,
        "parsed_at": pendulum.now("UTC"),
    }