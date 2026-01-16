import json
import time
import pexpect
from pathlib import Path
from typing import List, Dict, Any

class Recorder:
    def __init__(self, cols: int = 120, rows: int = 24):
        self.cols = cols
        self.rows = rows
        self.events: List[Dict[str, Any]] = []
        self.last_time = 0.0
        self.start_time = time.time()
        self.duration = 0.0

    class LogReader:
        """File-like for pexpect logfile_read: captures timed stdout chunks."""

        def __init__(self, recorder: 'Recorder'):
            self.recorder = recorder

        def write(self, chunk: str) -> None:
            if chunk:
                delta = time.time() - self.recorder.start_time - self.recorder.last_time
                self.recorder.events.append(
                    {
                        "time": max(0.0, delta),
                        "stdout": chunk,
                    }
                )
                self.recorder.last_time += delta
                self.recorder.duration = self.recorder.last_time

    def record(self, path: Path, shell: str = "bash") -> None:
        """Spawn interactive shell, record until exit."""
        child = pexpect.spawn(
            shell,
            encoding="utf-8",
            dimensions=(self.cols, self.rows),
            # env={"PS1": "REC> "},  # optional custom prompt
        )
        child.logfile_read = self.LogReader(self)
        print(
            "\n[bold green]Recording session...[/bold green] (Ctrl+D or 'exit' to stop)\n",
            file=sys.stderr,
        )
        child.interact()
        child.close(force=True)
        self._save(path)

    def _save(self, path: Path) -> None:
        metadata = {
            "version": 1,
            "width": self.cols,
            "height": self.rows,
            "duration": round(self.duration, 3),
            "timestamp": round(self.start_time, 3),
            "events_count": len(self.events),
        }
        data = [metadata] + self.events
        path.write_text(json.dumps(data, indent=2))
