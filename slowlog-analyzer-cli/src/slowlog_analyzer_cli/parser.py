import re
import sys
from pathlib import Path
from typing import Iterator, List, Optional, TextIO
from .models import SlowQuery


def detect_format(input_path: str, num_sample: int = 50) -> str:
    """Detect postgres or mysql from file sample."""
    if input_path == "-":
        raise ValueError("Cannot auto-detect on stdin; specify --format")
    path = Path(input_path)
    try:
        with open(path) as f:
            sample = [f.readline().strip() for _ in range(num_sample)]
    except:
        raise ValueError(f"Cannot read {input_path}")
    pg_hits = sum(1 for line in sample if "duration:" in line.lower())
    mysql_hits = sum(1 for line in sample if "# time:" in line.lower() or "# query_time:" in line.lower())
    return "postgres" if pg_hits >= mysql_hits else "mysql"


def extract_postgres(line: str) -> Optional[SlowQuery]:
    dur_match = re.search(r"duration:\s*([\d.]+)\s*ms", line, re.IGNORECASE)
    if not dur_match:
        return None
    duration_ms = float(dur_match.group(1))
    ts_match = re.search(r"(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2}\.\d{3})", line)
    timestamp = ts_match.group(1) if ts_match else "unknown"
    user_db_match = re.search(r"([\w-]+)@([\w-]+)", line)
    user, database = "", ""
    if user_db_match:
        user, database = user_db_match.groups()
    # Query: after duration or execute/ID:
    query_start = re.search(r"(?:duration|execute|statement):.*?([a-z]+\s+", line, re.IGNORECASE | re.DOTALL)
    query_match = re.search(r"(select|insert|update|delete|execute[^:]*:\s*)(.*)$", line, re.IGNORECASE | re.DOTALL)
    query = query_match.group(2).strip() if query_match else "unknown"
    return SlowQuery(timestamp, duration_ms, user, database, query)


def parse_mysql(lines: Iterator[str]) -> Iterator[SlowQuery]:
    current: dict = {}
    for line in lines:
        line = line.rstrip("\n")
        if not line or line.startswith("#"):
            if "query_time" in current:
                duration_ms = float(current["query_time"]) * 1000
                yield SlowQuery(
                    current.get("timestamp", "unknown"),
                    duration_ms,
                    current.get("user", ""),
                    current.get("database", ""),
                    current.get("query", "unknown"),
                )
                current = {}
            if line.startswith("# Time:"):
                current["timestamp"] = line[7:].strip()
            elif "User@Host:" in line:
                m = re.search(r"([\w-]+)\[([\w-]*?)\]", line)
                if m:
                    current["user"] = m.group(1)
                    current["database"] = m.group(2)
            elif "Query_time:" in line:
                m = re.search(r"Query_time:\s*([\d.]+)", line)
                if m:
                    current["query_time"] = m.group(1)
            continue
        # Query line
        current["query"] = line
    # Last query
    if "query_time" in current:
        duration_ms = float(current["query_time"]) * 1000
        yield SlowQuery(
            current.get("timestamp", "unknown"),
            duration_ms,
            current.get("user", ""),
            current.get("database", ""),
            current.get("query", "unknown"),
        )


def parse_log(input_path: str, fmt: str, min_duration: float = 0.0) -> List[SlowQuery]:
    """Parse log returning filtered queries."""
    queries: List[SlowQuery] = []
    if input_path == "-":
        lines = iter(sys.stdin.readline, "")
    else:
        with open(input_path) as f:
            lines = iter(f.readline, "")
    if fmt == "postgres":
        for line in lines:
            q = extract_postgres(line)
            if q and q.duration_ms >= min_duration:
                queries.append(q)
    elif fmt == "mysql":
        for q in parse_mysql(lines):
            if q.duration_ms >= min_duration:
                queries.append(q)
    return queries
