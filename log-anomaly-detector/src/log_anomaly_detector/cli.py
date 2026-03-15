import sys
import time
import yaml
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.traceback import install

import log_anomaly_detector

from . import config, parser, anomaly, visualizer

install(show_locals=True)

app = typer.Typer(name="log-anomaly", add_completion=False)
console = Console()


@app.command(help="Batch anomaly detection on JSONL file/stdin")
def batch(
    path: Optional[Path] = typer.Argument(None, help="Log file (default: stdin)"),
    config_path: Optional[Path] = typer.Option(
        None, "--config/-c", help="YAML config file"
    ),
    fields: list[str] = typer.Option([], "--field/-f", help="Numeric fields"),
    group_by: list[str] = typer.Option([], "--group-by/-g"),
    method: str = typer.Option("zscore", "--method/-m"),
    threshold: float = typer.Option(3.0, "--threshold/-t"),
    json_out: bool = typer.Option(False, "--json"),
):
    cfg_dict = {}
    if config_path:
        with open(config_path) as f:
            cfg_dict = yaml.safe_load(f) or {}

    cfg = config.AnomalyConfig(
        fields=fields or cfg_dict.get("fields", []),
        group_by=group_by or cfg_dict.get("group_by", []),
        method=cfg_dict.get("method", method),
        threshold=cfg_dict.get("threshold", threshold),
    )

    df = parser.parse_batch(None if path is None or path == Path("-") else str(path))
    anomalies = anomaly.find_anomalies(df, cfg)

    if json_out:
        print(anomalies.to_json(orient="records", lines=True, date_format="iso"), file=sys.stdout)
    else:
        visualizer.display_anomalies(anomalies, console)


@app.command(help="Live tail -f mode for ongoing logs")
def live(
    path: Path = typer.Argument(..., help="Log file to tail"),
    fields: list[str] = typer.Option(..., "--field/-f"),
    interval: float = typer.Option(1.0, "--interval/-i"),
    buffer_size: int = typer.Option(5000, "--buffer/-b"),
):
    """Live anomaly detection: tail -f equivalent."""
    pos = 0
    buffer = []
    cfg = config.AnomalyConfig(fields=fields)

    console.print(f"👀 Watching [bold]{path}[/bold] (buffer={buffer_size}, interval={interval}s)", justify="center")

    while True:
        try:
            st = path.stat()
            if st.st_size < pos:
                console.print("[yellow]Log rotated, resetting.[/yellow]")
                pos = 0
                buffer.clear()
            with open(path, "r") as f:
                f.seek(pos)
                new_lines = f.readlines()
                pos = f.tell()
            for line in new_lines:
                parsed = parser.parse_line(line)
                if parsed:
                    buffer.append(parsed)
                    if len(buffer) > buffer_size:
                        buffer.pop(0)
            if len(new_lines) > 0 and len(buffer) % 100 == 0:
                df = pd.DataFrame(buffer[-buffer_size:])
                anoms = anomaly.find_anomalies(df, cfg)
                if not anoms.empty:
                    console.print("\n[bold red]🚨 New Anomalies[/bold red]")
                    visualizer.display_anomalies(anoms.tail(5), console)
            time.sleep(interval)
        except KeyboardInterrupt:
            console.print("\n👋 Stopped.")
            break
        except FileNotFoundError:
            console.print("[red]File gone, retrying...[/red]")
            time.sleep(1)


if __name__ == "__main__":
    app()
