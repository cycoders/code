from pathlib import Path
from typing import List, Optional

import typer
import rich.console
import rich.table
import rich.panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
from rich import print as rprint

from ssh_config_visualizer.parser import load_ssh_config, get_all_host_sections, parse_config_content
from ssh_config_visualizer.graph_builder import build_ssh_graph
from ssh_config_visualizer.validator import validate_config
from ssh_config_visualizer.visualizer import render_mermaid, render_stats_table
from ssh_config_visualizer.tester import batch_test_connectivity

app = typer.Typer(add_completion=False)
console = rich.console.Console()

@app.command(help="Generate graph visualization of SSH config")
def graph(
    config: Path = typer.Argument(Path("~/.ssh/config"), help="Path to SSH config"),
    output: str = typer.Option("mermaid", "--output/-o", help="Output format: mermaid|stats"),
):
    """Visualize SSH config as Mermaid graph or stats."""
    try:
        ssh_cfg = load_ssh_config(str(config))
    except FileNotFoundError as e:
        typer.echo(f"[red]Error: {e}[/red]")
        raise typer.Exit(1)

    hosts = get_all_host_sections(ssh_cfg)
    G = build_ssh_graph(hosts)

    if output == "mermaid":
        mermaid_code = render_mermaid(G)
        console.print(
            rich.panel.Panel(
                mermaid_code,
                title="[bold cyan]Mermaid Graph[/]",
                border_style="cyan",
                expand=False,
            )
        )
        console.print("[italic blue]Paste into https://mermaid.live for interactive view![/]\n")
    elif output == "stats":
        render_stats_table(G, console)
    else:
        typer.echo("[red]Invalid output. Use 'mermaid' or 'stats'[/red]")
        raise typer.Exit(1)

@app.command(help="Validate SSH config for issues")
def validate(
    config: Path = typer.Argument(Path("~/.ssh/config")),
):
    """Check for cycles, duplicates, and config issues."""
    ssh_cfg = load_ssh_config(str(config))
    hosts = get_all_host_sections(ssh_cfg)
    G = build_ssh_graph(hosts)

    issues = validate_config(hosts, G)
    if issues:
        console.print("[bold red]Issues found:[/]\n")
        for issue in issues:
            console.print(f"  [red]✗[/] {issue}")
        raise typer.Exit(1)
    else:
        console.print("[bold green]✓ All good! No issues detected.[/]\n")

@app.command(help="Test connectivity to hosts")
def test(
    hosts: List[str] = typer.Argument(None, help="Hosts to test (auto from config if empty)"),
    config: Path = typer.Argument(Path("~/.ssh/config")),
    dry_run: bool = typer.Option(False, "--dry-run", help="Show commands only"),
    timeout: int = typer.Option(5, "--timeout", min=1, max=30),
):
    """Batch test SSH connectivity."""
    ssh_cfg_path = str(config.expanduser())
    if not hosts:
        ssh_cfg = load_ssh_config(ssh_cfg_path)
        hosts = [h.pattern for h in get_all_host_sections(ssh_cfg)]

    if dry_run:
        console.print("[yellow]Dry-run mode - no connections made.[/]\n")
        for h in hosts:
            console.print(f"ssh -F {ssh_cfg_path} -o BatchMode=yes -o ConnectTimeout={timeout} {h} -O check")
        return

    results = batch_test_connectivity(hosts, ssh_cfg_path, timeout)

    table = rich.table.Table(title="[bold]Connectivity Results[/]")
    table.add_column("Host", style="cyan")
    table.add_column("Status", style="green")
    table.add_column("Time", justify="right")

    success, fail = 0, 0
    for host, (status, elapsed) in results.items():
        mark = "[green]✓[/]" if status else "[red]✗[/]"
        table.add_row(host, mark, f"{elapsed:.1f}s")
        if status:
            success += 1
        else:
            fail += 1

    console.print(table)
    console.print(f"\n[bold]{success}/{len(hosts)} successful ({100*success/len(hosts):.0f}%)[/]")

if __name__ == "__main__":  # pragma: no cover
    app()