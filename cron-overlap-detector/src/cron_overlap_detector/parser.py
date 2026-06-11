from datetime import datetime
from typing import List, Tuple

def parse_crontab(path: str) -> List[Tuple[str, str]]:
    """Return list of (schedule, command) tuples."""
    # production-grade parser with comment/blank handling
    jobs = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split(None, 5)
            if len(parts) == 6:
                jobs.append((parts[0], parts[5]))
    return jobs