import json
import time
from pathlib import Path
from rich.console import Console
from rich import print as rprint

class Replayer:
    def __init__(self, path: Path):
        if not path.exists():
            raise FileNotFoundError(f"Session file not found: {path}")
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        self.metadata = data[0]
        self.events = data[1:]

    def run(self, speed: float = 1.0) -> None:
        """Replay stdout chunks with original deltas, ANSI preserved."""
        console = Console(width=self.metadata["width"], height=self.metadata["height"])
        last_t = 0.0
        for event in self.events:
            delta = event["time"] * speed
            time.sleep(delta)
            console.print(
                event["stdout"],
                end="",
                soft_wrap=True,
                markup=False,
                highlight=False,
            )
        rprint("\n[green bold]✓ Session replay complete[/green bold]")
