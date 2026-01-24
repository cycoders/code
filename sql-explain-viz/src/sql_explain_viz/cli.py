import typer
from pathlib import Path
import webbrowser

from rich.console import Console

from .parser import parse_explain

from .renderer import build_rich_tree, render_ascii, render_mermaid, render_svg

app = typer.Typer(add_completion=False)
console = Console()


@app.command(context_settings={"help_option_names": ["-h", "--help"]})
def viz(
    path: Path = typer.Argument(..., exists=True, help="EXPLAIN/ANALYZE output file"),
    fmt: str = typer.Option("rich", "-f", "--format", help="rich|ascii|mermaid|svg"),
    db: str = typer.Option("auto", "-d", "--db", help="postgres|sqlite|mysql|auto"),
    output: Optional[Path] = typer.Option(None, "-o", "--output", writable=True),
    open_browser: bool = typer.Option(False, "-O", "--open"),
):
    """Visualize SQL query plan."""

    typer.echo(f"[bold green]Parsing[/]: {path}", err=True)
    with console.status("[bold blue]Building tree..."):
        content = path.read_text(errors="ignore")
        node = parse_explain(content, db)

    if fmt == "rich":
        if output:
            typer.echo("[yellow]Rich is terminal-only, saving ASCII instead.[/]", err=True)
            fmt = "ascii"
        tree = build_rich_tree(node)
        console.print(tree)
        return

    # String-based formats
    if fmt == "ascii":
        text = render_ascii(node)
    elif fmt == "mermaid":
        text = f"```mermaid\n{render_mermaid(node)}\n```"
    else:
        assert fmt == "svg"
        if not output:
            raise typer.BadParameter("SVG requires --output")
        render_svg(node, str(output))
        typer.echo(f"[green]Saved SVG:[/] {output}")
        if open_browser:
            webbrowser.open(f"file://{output.resolve()}")
        return

    # Save/print text
    if output:
        output.write_text(text)
        typer.echo(f"[green]Saved:[/] {output}")
    else:
        console.print(text)