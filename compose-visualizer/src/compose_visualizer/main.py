import typer

from pathlib import Path

from rich.console import Console

import webbrowser

try:
    from .parser import parse_compose
    from .graph import build_graph, find_cycles
    from .auditor import audit_compose
    from .renderer import generate_mermaid, services_table, render_visualize
except ImportError:
    # For dev
    from parser import parse_compose
    from graph import build_graph, find_cycles
    from auditor import audit_compose
    from renderer import generate_mermaid, services_table, render_visualize


app = typer.Typer(add_completion=False)
console = Console()


@app.command(help="Visualize dependencies as Mermaid graph + table")
def visualize(
    compose_file: Path = typer.Argument(Path("docker-compose.yml")),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Save Mermaid"),
    open_browser: bool = typer.Option(False, "--open", help="Open Mermaid in browser"),
):
    try:
        compose = parse_compose(compose_file)
        graph = build_graph(compose.services)
        cycles = find_cycles(graph)

        if cycles:
            console.print("[bold red]⚠ Cycles detected:[/]\n")
            for cycle in cycles:
                console.print(f"  [red]{' -> '.join(cycle)} → {cycle[0]}[/]")

        mermaid_code = generate_mermaid(graph, compose.services)
        render_visualize(graph, compose.services, mermaid_code)

        if output:
            output.write_text(mermaid_code)
            console.print(f"[green]✓ Saved Mermaid to {output}[/]\n")

        if open_browser:
            # Simple HTML wrapper for mermaid.live compat
            html = f'''<html><body><script src="https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.min.js"></script><div class="mermaid">{mermaid_code}</div><script>mermaid.initialize({{startOnLoad:true}});</script></body></html>'''
            temp_html = compose_file.parent / "temp-viz.html"
            temp_html.write_text(html)
            webbrowser.open(f"file://{temp_html.absolute()}")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/]")
        raise typer.Exit(1)


@app.command(help="Audit for issues: cycles, ports, orphans, unused resources")
def audit(
    compose_file: Path = typer.Argument(Path("docker-compose.yml")),
):
    try:
        compose = parse_compose(compose_file)
        issues = audit_compose(compose)

        if not issues:
            console.print("[bold green]✓ Clean bill of health![/]\n")
        else:
            console.print(f"[bold red]Found {len(issues)} issues:[/]\n")
            for issue in issues:
                console.print(f"  [yellow]⚠  {issue}[/]\n")

    except Exception as e:
        console.print(f"[red]Error: {str(e)}[/]")
        raise typer.Exit(1)


if __name__ == "__main__":
    app()