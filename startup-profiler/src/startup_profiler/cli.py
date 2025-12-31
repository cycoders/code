import json
import os
import sys
import tempfile
from pathlib import Path
from typing import Any

import typer
from rich.console import Console
import webbrowser

from startup_profiler.profiler import ImportProfiler
from startup_profiler.runner import main as runner_main
from startup_profiler.visualizer import render_table, render_flamegraph_svg, render_html_report

app = typer.Typer(add_completion=False)
console = Console()

@app.command(help="Analyze startup imports of a Python script")
def analyze(
    script: Path = typer.Argument(..., exists=True, help="Python script to profile"),
    output: Path = typer.Option(Path.cwd(), "--output", "-o", help="Output directory"),
    fmt: str = typer.Option("table", "--format", "-f", choices=["table", "json", "html", "svg"], help="Output format"),
    thirdparty_only: bool = typer.Option(False, "--thirdparty-only", help="Filter to non-stdlib"),
    timeout: float = typer.Option(30.0, "--timeout", help="Subprocess timeout (s)"),
) -> None:
    """Profile startup imports."""
    output.mkdir(parents=True, exist_ok=True)
    output_file = tempfile.mktemp(suffix=".json", dir=str(Path(tempfile.gettempdir())))
    env = os.environ.copy()
    env["STARTUP_PROFILER_OUTPUT"] = output_file
    cmd = [sys.executable, "-m", "startup_profiler.runner", str(script.resolve())]
    try:
        proc = subprocess.run(cmd, env=env, timeout=timeout, capture_output=True, text=True)
        if proc.returncode != 0:
            console.print(f"[red]Runner error:[/red] {proc.stderr.strip()}")
            raise typer.Exit(code=1)
    except subprocess.TimeoutExpired:
        console.print("[red]Timeout: Startup > timeout. Consider lazy imports.[/red]")
        return

    try:
        with open(output_file) as f:
            data = json.loads(f.read())
    except (FileNotFoundError, json.JSONDecodeError) as e:
        console.print(f"[red]Failed to read results: {e}[/red]")
        return
    finally:
        try:
            os.unlink(output_file)
        except OSError:
            pass

    if "error" in data:
        console.print(f"[red]Script error:[/red]\n{data['error']}")
        if "traceback" in data:
            console.print("[dim]Traceback:[/dim]\n" + data["traceback"])
        return

    timings: Dict[str, Any] = data
    if thirdparty_only:
        timings = {k: v for k, v in timings.items() if k != "_meta" and not v.get("is_stdlib", False)}

    if fmt == "json":
        json_path = output / "timings.json"
        with open(json_path, "w") as f:
            json.dump(timings, f, indent=2)
        console.print(f"[green]JSON:[/green] {json_path}")
    elif fmt == "svg":
        svg_content = render_flamegraph_svg(timings)
        svg_path = output / "flamegraph.svg"
        with open(svg_path, "w") as f:
            f.write(svg_content)
        console.print(f"[green]SVG:[/green] {svg_path}")
    elif fmt == "html":
        html_content = render_html_report(timings)
        html_path = output / "report.html"
        with open(html_path, "w") as f:
            f.write(html_content)
        console.print(f"[green]HTML:[/green] {html_path}")
        webbrowser.open(f"file://{html_path.absolute()}")
    else:  # table
        render_table(timings, console)
        svg_path = output / "flamegraph.svg"
        svg_content = render_flamegraph_svg(timings)
        with open(svg_path, "w") as f:
            f.write(svg_content)
        console.print(f"\n[blue]🔥 Flamegraph:[/blue] {svg_path}")


if __name__ == "__main__":
    app()
