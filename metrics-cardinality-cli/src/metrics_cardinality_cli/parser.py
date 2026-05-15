from __future__ import annotations
import re
from collections import defaultdict
from typing import Iterator

METRIC_RE = re.compile(r"^([a-zA-Z_:][a-zA-Z0-9_:]*)(\{.*\})?\s+([0-9.eE+-]+)")
LABEL_RE = re.compile(r"(\w+)="([^"\\]*(?:\\.[^"\\]*)*)")


def parse_exposition(lines: Iterator[str]) -> Iterator[dict]:
    for line in lines:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        m = METRIC_RE.match(line)
        if not m:
            continue
        name, labels, _ = m.groups()
        label_dict = {}
        if labels:
            for lm in LABEL_RE.finditer(labels):
                label_dict[lm.group(1)] = lm.group(2)
        yield {"name": name, "labels": label_dict}