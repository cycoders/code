import typer
from typing import Annotated, Literal
from rich import print as rprint
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

import ab_test_calculator_cli.stats as stats
from ab_test_calculator_cli.stats import AnalysisResult, DesignResult

cli = typer.Typer(add_completion=False)
console = Console()

@cli.command(name="design")
def design_sample_size(
    metric: Literal["prop", "mean"] = "prop",
    baseline: Annotated[float, typer.Argument(..., help="Baseline rate/mean")] = 0.0,
    mde: Annotated[float, typer.Argument(..., help="Minimum detectable effect (absolute)")] = 0.0,
    stddev: Annotated[float, typer.Argument(0.0, help="Stddev (required for means)")] = 0.0,
    alpha: Annotated[float, typer.Argument(0.05, help="Significance level")] = 0.05,
    power: Annotated[float, typer.Argument(0.8, help="Statistical power (1-beta)")] = 0.8,
    ratio: Annotated[float, typer.Argument(1.0, help="B/A sample ratio")] = 1.0,
    export: str = typer.Option("", help="Export to csv/json"),
) -> None:
    """Calculate required sample sizes for A/B test."""

    try:
        if metric == "prop":
            if not 0 < baseline < 1:
                raise typer.BadParameter("Baseline must be in (0,1) for proportions")
            result: DesignResult = stats.design_proportion(baseline, mde, alpha, power, ratio)
        elif metric == "mean":
            if stddev <= 0:
                raise typer.BadParameter("Stddev >0 required for means")
            result = stats.design_mean(baseline, mde, stddev, alpha, power, ratio)
        else:
            raise ValueError(f"Unknown metric: {metric}")

        table = Table(title="[bold cyan]Sample Size Calculation[/bold cyan]", box=None)
        table.add_column("Group", style="cyan")
        table.add_column("N", justify="right", style="magenta")
        table.add_row("Control (A)", f"{result.n_a:,}")
        table.add_row("Treatment (B)", f"{result.n_b:,}")
        table.add_row("[bold]Total[/bold]", f"[bold]{result.total:,}[/bold]")
        table.add_row("Effect Size", f"{result.effect_size:.4f}")

        console.print(table)

        if result.warning:
            console.print(Panel(result.warning, title="⚠️  Warning", border_style="yellow"))

        if export:
            # Simple CSV export
            import csv
            with open(export, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["group", "n"])
                writer.writerow(["A", result.n_a])
                writer.writerow(["B", result.n_b])
            rprint(f"[green]Exported to {export}[/green]")

    except ValueError as e:
        typer.echo(f"[red]Error: {e}[/red]", err=True)
        raise typer.Exit(1)

@cli.command()
def analyze_proportion(
    a_success: Annotated[int, typer.Argument(..., help="Control successes")],
    a_total: Annotated[int, typer.Argument(..., help="Control trials")],
    b_success: Annotated[int, typer.Argument(..., help="Treatment successes")],
    b_total: Annotated[int, typer.Argument(..., help="Treatment trials")],
    alpha: Annotated[float, typer.Argument(0.05)] = 0.05,
    prior_strength: Annotated[float, typer.Argument(1.0, help="Bayes prior pseudo-counts")] = 1.0,
    mc_samples: Annotated[int, typer.Argument(100_000)] = 100_000,
    export: str = typer.Option(""),
) -> None:
    """Analyze proportion A/B test (frequentist + Bayesian)."""

    if a_total == 0 or b_total == 0:
        raise typer.BadParameter("Totals must be >0")

    result: AnalysisResult = stats.analyze_proportion(
        a_success, a_total, b_success, b_total, alpha, prior_strength, mc_samples
    )

    table = Table(title="[bold cyan]A/B Test Analysis[/bold cyan]", box=None, expand=True)
    table.add_column("Metric", style="cyan", no_wrap=True)
    table.add_column("Control (A)", justify="right")
    table.add_column("Treatment (B)", justify="right")

    rate_a = a_success / a_total
    rate_b = b_success / b_total
    lift = (rate_b - rate_a) / rate_a * 100 if rate_a > 0 else 0

    table.add_row("Observed Rate", f"{rate_a:.1%}", f"{rate_b:.1%}")
    table.add_row("Lift", "", f"{lift:.1f}%")
    table.add_row("p-value", "", f"{result.p_value:.4f}")
    table.add_row("95% CI", f"{result.ci_a}", f"{result.ci_b}")
    table.add_row("Bayes P(B>A)", "", f"{result.prob_b_superior:.1%}")
    table.add_row("Bayes Lift (mean)", "", f"{result.bayes_lift:.1%}")

    console.print(table)

    if result.warning:
        console.print(Panel(result.warning, title="⚠️  Advisory", border_style="yellow"))

    if export == "csv":
        typer.echo("group,rate,pvalue,ci_low,ci_high,prob_b_better,bayes_lift")
        typer.echo(f"A,{rate_a:.4f},,,{result.ci_a[0]:.4f}-{result.ci_a[1]:.4f},,")
        typer.echo(f"B,{rate_b:.4f},{result.p_value:.4f},{result.ci_b[0]:.4f},{result.ci_b[1]:.4f},{result.prob_b_superior:.4f},{result.bayes_lift:.4f}")

def main():
    if __name__ == "__main__":
        cli()