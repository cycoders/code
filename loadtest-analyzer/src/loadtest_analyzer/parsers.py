import csv
import json
from datetime import datetime
from typing import Iterator, Dict, Any, Optional
from pathlib import Path

from .models import Request


def parse_timestamp(ts_str: str) -> float:
    """Parse timestamp as unix float or ISO datetime."""
    try:
        return float(ts_str)
    except ValueError:
        try:
            # Handle ISO with optional Z
            if ts_str.endswith('Z'):
                ts_str = ts_str[:-1] + '+00:00'
            return datetime.fromisoformat(ts_str).timestamp()
        except ValueError:
            raise ValueError(f"Invalid timestamp format: {ts_str}")


def parse_csv(filepath: str, field_map: Dict[str, str]) -> Iterator[Request]:
    """Parse CSV file yielding Request objects, skipping invalid rows."""
    filepath = Path(filepath)
    with filepath.open('r') as f:
        reader = csv.DictReader(f)
        for row_num, row in enumerate(reader, start=2):  # 1-indexed
            try:
                ts = parse_timestamp(row[field_map['ts']])
                duration = float(row[field_map['duration']])
                status = int(row.get(field_map['status'], '200'))
                endpoint = row[field_map['endpoint']]
                method = row.get(field_map['method'], 'GET')
                error = row.get(field_map['error'])
                if error == '':
                    error = None
                yield Request(ts, duration, status, endpoint, method, error)
            except (KeyError, ValueError, IndexError) as e:
                print(f"Skipping row {row_num}: {e}", file=Path.devnull)  # Silent
                continue


def parse_json(filepath: str, field_map: Dict[str, str]) -> Iterator[Request]:
    """Parse JSON array of dicts yielding Request objects."""
    filepath = Path(filepath)
    data = json.loads(filepath.read_text())
    if isinstance(data, list):
        for row in data:
            try:
                ts = parse_timestamp(row[field_map['ts']])
                duration = float(row[field_map['duration']])
                status = int(row.get(field_map['status'], 200))
                endpoint = row[field_map['endpoint']]
                method = row.get(field_map['method'], 'GET')
                error = row.get(field_map['error'])
                yield Request(ts, duration, status, endpoint, method, error)
            except (KeyError, ValueError) as e:
                print(f"Skipping JSON row: {e}", file=Path.devnull)
                continue
    else:
        raise ValueError("JSON must be an array of objects")


def parse_jsonl(filepath: str, field_map: Dict[str, str]) -> Iterator[Request]:
    """Parse JSONL (one JSON object per line)."""
    filepath = Path(filepath)
    with filepath.open('r') as f:
        for line_num, line in enumerate(f, start=1):
            try:
                row = json.loads(line)
                ts = parse_timestamp(row[field_map['ts']])
                duration = float(row[field_map['duration']])
                status = int(row.get(field_map['status'], 200))
                endpoint = row[field_map['endpoint']]
                method = row.get(field_map['method'], 'GET')
                error = row.get(field_map['error'])
                yield Request(ts, duration, status, endpoint, method, error)
            except (json.JSONDecodeError, KeyError, ValueError) as e:
                print(f"Skipping JSONL line {line_num}: {e}", file=Path.devnull)
                continue
