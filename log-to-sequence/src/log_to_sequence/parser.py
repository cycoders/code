import json
from collections import defaultdict
from pathlib import Path
from typing import Dict, List

from dateutil import parser

import log_to_sequence.models as models


def parse_timestamp(ts_str: str) -> models.datetime:
    return parser.parse(ts_str)


def parse_log_file(path: Path, config: models.Config) -> Dict[str, List[models.LogEntry]]:
    traces: Dict[str, List[models.LogEntry]] = defaultdict(list)
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except Exception:
        return {}

    for line_num, line in enumerate(lines, 1):
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
            ts_str = row.get(config.fields["timestamp"], "")
            if not ts_str:
                continue

            entry = models.LogEntry(
                timestamp=parse_timestamp(ts_str),
                trace_id=row[config.fields["trace_id"]],
                span_id=row[config.fields["span_id"]],
                parent_span_id=row.get(config.fields["parent_span_id"]),
                service=row[config.fields["service"]],
                name=row.get(config.fields["name"], "unknown"),
                duration_ms=row.get(config.fields["duration_ms"]),
            )
            traces[entry.trace_id].append(entry)
        except (KeyError, ValueError, json.JSONDecodeError, TypeError) as e:
            print(f"Skipping line {line_num}: {e}")
            continue

    # Sort entries per trace by timestamp
    for trace_id in traces:
        traces[trace_id] = sorted(traces[trace_id], key=lambda e: e.timestamp)

    return dict(traces)