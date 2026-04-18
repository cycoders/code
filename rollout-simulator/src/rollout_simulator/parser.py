import json
from pathlib import Path
from typing import List

import numpy as np  # for std
from .types import MetricEntry, DeployMetrics


def parse_metrics(file_path: Path) -> List[MetricEntry]:
    """Parse JSONL metrics file into MetricEntry list."""
    entries: List[MetricEntry] = []
    try:
        with file_path.open('r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry_dict = json.loads(line)
                    entry = MetricEntry.model_validate(entry_dict)
                    entries.append(entry)
                except (json.JSONDecodeError, ValueError) as e:
                    raise ValueError(f'Invalid data at line {line_num}: {e}')
    except FileNotFoundError:
        raise FileNotFoundError(f'Metrics file not found: {file_path}')

    if not entries:
        raise ValueError('No valid metrics entries found')

    return entries


def group_by_deploy(entries: List[MetricEntry]) -> List[DeployMetrics]:
    """Group entries by deploy_id, compute aggregates, sort by last_ts."""
    deploy_dict: dict[str, List[MetricEntry]] = {}
    for entry in entries:
        deploy_dict.setdefault(entry.deploy_id, []).append(entry)

    deploys: List[DeployMetrics] = []
    for did, elist in deploy_dict.items():
        elist.sort(key=lambda e: e.timestamp)
        rates = np.array([e.error_rate for e in elist])
        avg_rate = float(np.mean(rates))
        std_rate = float(np.std(rates)) if len(rates) > 1 else 0.0
        deploys.append(DeployMetrics(
            deploy_id=did,
            avg_error_rate=avg_rate,
            std_error_rate=std_rate,
            num_entries=len(elist),
            first_ts=elist[0].timestamp,
            last_ts=elist[-1].timestamp,
        ))

    deploys.sort(key=lambda d: d.last_ts)
    return deploys