import re
from collections import Counter
from pathlib import Path

def infer_schema(log_dir: str):
    """Infer schema with type detection and confidence scores."""
    patterns = []
    for file in Path(log_dir).glob("*.log"):
        for line in file.read_text().splitlines()[:1000]:
            patterns.append(_detect_pattern(line))
    return {"fields": _merge_patterns(patterns)}

def _detect_pattern(line: str):
    if re.match(r"^\d{4}-\d{2}-\d{2}", line):
        return {"ts": "datetime", "msg": "str"}
    if "=" in line:
        return {k: "str" for k in re.findall(r"(\w+)=", line)}
    return {"raw": "str"}

def _merge_patterns(patterns):
    field_counts = Counter()
    for p in patterns:
        for f in p:
            field_counts[f] += 1
    return {f: {"type": "str", "confidence": c / len(patterns)} for f, c in field_counts.items()}