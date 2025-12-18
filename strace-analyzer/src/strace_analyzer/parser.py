import re
import logging
from pathlib import Path
from typing import Iterator, List, Optional

from .models import StraceEvent

logger = logging.getLogger(__name__)

_SYSCALL_RE = re.compile(
    r"^(\d+)\s+([\d.]+)\s+([^(\]]+)\s*\(\s*(.*?)\s*\)\s*=\s*(.*?)\s*(?:<([\d.]+)>\)?.*?(.*)?$",
    re.IGNORECASE,
)

_EXIT_RE = re.compile(r"^(\d+)\s+[\d.]+\s+\+\+\+\s+exited\s+with\s+(\d+)\s+\+\+\+")


def parse_strace(filename: str | Path) -> List[StraceEvent]:
    """Parse strace log file into list of events."""
    events: List[StraceEvent] = []
    path = Path(filename)
    if not path.exists():
        raise FileNotFoundError(f"Strace log not found: {path}")

    with path.open() as f:
        for line_num, line in enumerate(f, 1):
            line = line.strip()
            if not line or line.startswith("strace:"):
                continue

            event = _parse_line(line)
            if event:
                events.append(event)
            else:
                logger.debug("Unparsed line %d: %s", line_num, line[:100])

    logger.info("Parsed %d events from %s", len(events), path)
    return events


def _parse_line(line: str) -> Optional[StraceEvent]:
    # Handle exit lines
    exit_match = _EXIT_RE.match(line)
    if exit_match:
        pid, code = map(int, exit_match.groups())
        return StraceEvent(0.0, pid, "exit", [], str(code), None, None)

    # Handle syscall lines
    match = _SYSCALL_RE.match(line)
    if match:
        pid, start_time, syscall, args_str, result, duration_str, notes = match.groups()
        args = [arg.strip() for arg in args_str.split(",") if arg.strip()]
        duration = float(duration_str) if duration_str else None
        return StraceEvent(
            float(start_time),
            int(pid),
            syscall.strip(),
            args,
            result.strip(),
            duration,
            (notes or "").strip() or None,
        )
    return None
