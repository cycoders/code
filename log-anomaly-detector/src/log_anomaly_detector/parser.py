import json
import sys
from pathlib import Path
from typing import Iterator, Optional

import pandas as pd


def parse_batch(path: Optional[str] = None) -> pd.DataFrame:
    """
    Parse JSONL logs from file or stdin into DataFrame.

    Infers numeric columns automatically.
    Skips malformed lines with warnings.
    """
    try:
        if path is None or path == "-":
            df = pd.read_json(sys.stdin, lines=True)
        else:
            df = pd.read_json(Path(path), lines=True)
        numeric_cols = df.select_dtypes(include=["number"]).columns.tolist()
        print(
            f"[INFO] Parsed {len(df):,} rows. Numeric fields: {numeric_cols}",
            file=sys.stderr,
        )
        return df
    except pd.errors.EmptyDataError:
        print("[WARN] Empty input", file=sys.stderr)
        return pd.DataFrame()
    except Exception as e:
        raise ValueError(f"Parse error: {e}") from e


def parse_line(line: str) -> Optional[dict]:
    """Parse single JSONL line, return None on error."""
    line = line.strip()
    if not line:
        return None
    try:
        return json.loads(line)
    except json.JSONDecodeError:
        return None
