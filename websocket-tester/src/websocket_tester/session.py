import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Iterator, List

SessionEntry = Dict[str, Any]

JSONL_MODE = "w"

class SessionManager:
    """Handle session save/load as JSONL."""

    @staticmethod
    def new_entry(direction: str, payload: Any, ts: Optional[str] = None) -> SessionEntry:
        return {
            "ts": ts or datetime.now().isoformat(),
            "direction": direction,
            "payload": payload,
        }

    @staticmethod
    def save(entries: List[SessionEntry], path: Path) -> None:
        """Dump entries to JSONL."""
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("w", encoding="utf-8") as f:
            for entry in entries:
                json.dump(entry, f, ensure_ascii=False, separators=(",", ":"))
                f.write("\n")

    @staticmethod
    def load(path: Path) -> Iterator[SessionEntry]:
        """Yield entries from JSONL."""
        try:
            with path.open(encoding="utf-8") as f:
                for line in f:
                    yield json.loads(line.strip())
        except (json.JSONDecodeError, FileNotFoundError) as e:
            raise ValueError(f"Invalid session file {path}: {e}")