import sys
import typer
from pathlib import Path
from rich.console import Console
from rich.traceback import install as rich_traceback
from . import __version__
from .config import get_default_config_path, load_config, Config
from .parsers import detect_language, parse
from .core import collapse_frames
from .models import Stacktrace, Frame
from .renderer import render_terminal, render_html, render_json


app = typer.Typer(no_args_is_help=True)
console = Console()
rich_traceback(console=console, suppress=[typer.core.TyperInvocation])


@app.command()
def main(
    file: Path = typer.Argument(None, help="Input file (default: stdin)"),
    format: str = typer.Option("terminal", "-f", "--format", help="Output: terminal|html|json"),
    open_browser: bool = typer.Option(False, "--open-browser", help="Open HTML in browser"),
    config: Path = typer.Option(None, "--config", help="Custom config.toml"),
) -> None:
    """Collapse & beautify stack traces from stdin/file."""

    # Read content
    if file:
        content = file.read_text(errors="ignore")
    else:
        content = sys.stdin.read().strip()
    if not content:
        typer.echo("No input provided.", err=True)
        raise typer.Exit(1)

    try:
        # Parse
        language = detect_language(content)
        frames: list[Frame] = parse(content, language)
        st = Stacktrace(language=language, frames=frames)

        # Config
        cfg_path = config or get_default_config_path()
        cfg = load_config(cfg_path)

        # Collapse
        collapsed_frames = collapse_frames(st.frames, cfg.collapse_threshold)
        st.frames = collapsed_frames

        # Render
        match format.lower():
            case "terminal":
                render_terminal(st.frames, st.language, console)
            case "html":
                html = render_html(st.frames, st.language)
                if open_browser:
                    with tempfile.NamedTemporaryFile(mode="w", suffix=".html", delete=False) as tmp:
                        tmp.write(html)
                        tmp_path = Path(tmp.name)
                    webbrowser.open(f"file://{os.path.abspath(tmp_path)}")
                else:
                    console.print(html)
            case "json":
                console.print(render_json(st))
            case _:
                typer.echo(f"Unknown format: {format}", err=True)
                raise typer.Exit(1)

    except Exception as e:
        typer.echo(f"Error: {str(e)}", err=True)
        raise typer.Exit(1)


@app.command()
def version():
    typer.echo(f"stacktrace-collapser {__version__}")


if __name__ == "__main__":
    app()
