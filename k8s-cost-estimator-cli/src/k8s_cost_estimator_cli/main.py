import click
import sys
from pathlib import Path
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from .manifest_scanner import scan_manifests
from .cost_calculator import calculate_costs
from .table_renderer import render_table
from .types import Config, CostBreakdown


console = Console()


@click.group()
@click.version_option(prog_name="k8s-cost-estimator-cli")
def cli():
    """Estimate Kubernetes costs from YAML manifests."""
    pass


@cli.command()
@click.argument("path", type=click.Path(exists=True, path_type=Path))
@click.option("--provider", "provider", type=click.Choice(["aws", "gcp", "azure"]), required=True)
@click.option("--region", required=True, help="Cloud region (e.g., us-east-1)")
@click.option("--nodes", type=int, default=3, help="Cluster node count for DaemonSets")
@click.option("--utilization", type=float, default=1.0, help="Utilization factor (0.5-1.0)")
@click.option("--days", type=int, default=30, help="Billing days per month")
@click.option("--output", "output_fmt", type=click.Choice(["table", "json"]), default="table")
@click.option("--quiet", "quiet", is_flag=True)
def scan(
    path: Path,
    provider: str,
    region: str,
    nodes: int,
    utilization: float,
    days: int,
    output_fmt: str,
    quiet: bool,
):
    """Scan directory for K8s YAMLs and estimate costs."""
    if not quiet:
        console.print(f"[bold blue]Scanning {path} for manifests...[/]")

    cfg = Config(
        provider=provider,
        region=region,
        nodes=nodes,
        utilization=utilization,
        days=days,
    )

    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("Analyzing...", total=None)
        breakdowns: list[CostBreakdown] = []
        try:
            manifests = scan_manifests(path)
            progress.update(task, description="Parsing manifests...")
            for manifest in manifests:
                breakdown = calculate_costs(manifest, cfg)
                if breakdown.total_cost > 0:
                    breakdowns.append(breakdown)
            progress.update(task, description="Rendering...")
        except Exception as e:
            console.print(f"[red]Error: {e}[/]")
            sys.exit(1)

    if output_fmt == "table":
        render_table(breakdowns, cfg)
    else:
        import json
        console.print(json.dumps([b.model_dump() for b in breakdowns], indent=2))


if __name__ == "__main__":
    cli()
