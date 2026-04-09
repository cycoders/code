import csv
import json
from pathlib import Path
from typing import Iterator, Tuple


def load_trace(file_path: Path) -> Iterator[Tuple[str, int]]:
    """
    Load access trace from JSONL or CSV.

    JSONL: {"key": "str", "size": int} per line
    CSV: header 'key,size'
    Skips invalid lines gracefully.
    """
    suffix = file_path.suffix.lower()
    if suffix == ".jsonl":
        with file_path.open("r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    data = json.loads(line)
                    yield data["key"], int(data["size"])
                except (json.JSONDecodeError, KeyError, ValueError, TypeError):
                    continue  # Silent skip
    elif suffix == ".csv":
        with file_path.open("r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                try:
                    yield row["key"], int(row["size"])
                except (KeyError, ValueError):
                    continue
    else:
        raise ValueError(f"Unsupported format: {suffix}. Use .jsonl or .csv")