import typer
from pathlib import Path
import sys

from rich.console import Console
from rich import print as rprint

from shell_recorder_cli.recorder import Recorder
from shell_recorder_cli.replayer import Replayer
from shell_recorder_cli.exporter import export_md
from shell_recorder_cli.redactor import redact_session
from shell_recorder_cli.editor import delete_lines, parse_line_ranges

app = typer.Typer(add_completion=False)
console = Console()

@app.command(help="Record an interactive shell session")
def record(
    path: Path = typer.Argument(Path("session.shellrec"), help="Output file"),
    shell: str = typer.Option("bash", "--shell", help="Shell to spawn (bash/zsh)"),
    cols: int = typer.Option(120, "--cols", min=80, max=200, help="Terminal width"),
    rows: int = typer.Option(24, "--rows", min=20, max=50, help="Terminal height"),
):
    """Record terminal output with timings. Interact, then exit."""
    try:
        rec = Recorder(cols, rows)
        rec.record(path, shell)
        rprint(f"[green]✓ Recorded to {path} ({rec.duration:.1f}s, {len(rec.events)} chunks)"]
    except KeyboardInterrupt:
        rprint("[yellow]Recording interrupted.")
        sys.exit(1)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(1)

@app.command(help="Replay a recorded session")
def replay(
    path: Path = typer.Argument(..., exists=True, help="Session file"),
    speed: float = typer.Option(1.0, "--speed", min=0.1, max=100.0, help="Playback speed multiplier"),
):
    """Replay session in terminal with timings."""
    try:
        r = Replayer(path)
        r.run(speed)
    except FileNotFoundError:
        typer.echo(f"File not found: {path}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Replay error: {e}", err=True)
        raise typer.Exit(1)

@app.command(help="Export session to Markdown")
def export(
    path: Path = typer.Argument(..., exists=True, help="Session file"),
    output: Path = typer.Option(Path("session.md"), "--output/-o", help="Output MD file"),
    title: str = typer.Option("Terminal Session", "--title", help="MD heading"),
):
    """Export full stdout to copy-pasteable bash code block."""
    try:
        export_md(path, output, title)
        rprint(f"[green]✓ Exported to {output}")
    except Exception as e:
        typer.echo(f"Export error: {e}", err=True)
        raise typer.Exit(1)

@app.command(help="Redact PII from session")
def redact(
    path: Path = typer.Argument(..., exists=True, help="Input session"),
    output: Path = typer.Option(Path("redacted.shellrec"), "--output/-o", help="Output file"),
):
    """Redact IPs, emails, dates with [REDACTED]."""
    try:
        redact_session(path, output)
        rprint(f"[green]✓ Redacted to {output}")
    except Exception as e:
        typer.echo(f"Redact error: {e}", err=True)
        raise typer.Exit(1)

@app.command(help="Delete specific lines")
def delete(
    path: Path = typer.Argument(..., exists=True, help="Input session"),
    lines: str = typer.Argument(..., help="Lines to delete (1-indexed): 2,5-7,10"),
    output: Path = typer.Option(Path("edited.shellrec"), "--output/-o"),
):
    """Delete lines by comma-separated indices/ranges."""
    try:
        indices = parse_line_ranges(lines)
        if not indices:
            rprint("[yellow]No lines specified.")
            return
        delete_lines(path, output, indices)
        rprint(f"[green]✓ Deleted {len(indices)} lines to {output}")
    except ValueError as e:
        typer.echo(f"Invalid lines: {e}", err=True)
        raise typer.Exit(1)
    except Exception as e:
        typer.echo(f"Delete error: {e}", err=True)
        raise typer.Exit(1)

@app.command(help="Preview session stdout")
def preview(path: Path = typer.Argument(..., exists=True)):
    """Print full stdout transcript."""
    try:
        with open(path) as f:
            data = json.load(f)
        stdout_all = "".join(e["stdout"] for e in data[1:])
        console.print(stdout_all, markup=False, soft_wrap=True)
    except Exception as e:
        typer.echo(f"Preview error: {e}", err=True)
        raise typer.Exit(1)

if __name__ == "__main__":
    app(prog_name="shell-recorder-cli")
