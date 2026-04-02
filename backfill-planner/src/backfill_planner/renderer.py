from rich.console import Console, Panel
from rich.table import Table
from rich.text import Text
from rich import box

from .plan import Plan


def render_plan(plan: Plan, console: Console):
    """Render beautiful plan report."""

    # Summary
    summary = Text()
    summary.append(f"Strategy: [bold cyan]{plan.strategy}[/bold cyan] ({plan.dialect})\n")
    summary.append(f"Rows: [bold]{plan.total_rows:,}[/bold] | Batch: [bold]{plan.optimal_batch_size:,}[/bold] rows\n")
    summary.append(f"Est. time: [bold green]{plan.total_est_time_hours:.2f}h[/bold green] | Risk: [bold { 'green' if plan.risk_score=='LOW' else 'yellow' if plan.risk_score=='MEDIUM' else 'red' }]{plan.risk_score}[/bold { 'green' if plan.risk_score=='LOW' else 'yellow' if plan.risk_score=='MEDIUM' else 'red' }]\n")

    console.print(Panel(summary, title="[bold white]Backfill Plan[/bold white]", border_style="blue"))

    # Phases table
    table = Table(title="Phases", box=box.ROUNDED)
    table.add_column("Phase", style="cyan", no_wrap=True)
    table.add_column("Duration (h)", justify="right")
    table.add_column("Batches", justify="right")
    table.add_column("SQL Snippet", ratio=2)

    for phase in plan.phases:
        table.add_row(
            phase.name,
            f"{phase.est_duration_hours:.2f}",
            str(phase.batches),
            Text(phase.sql_snippet, style="dim"),
        )

    console.print(table)

    # Risks & Recs
    if plan.recommendations:
        rec_table = Table.grid(expand=True)
        rec_table.add_column("Recommendations", style="green")
        for rec in plan.recommendations:
            rec_table.add_row(rec)
        console.print(Panel(rec_table, title="Tips", border_style="green"))

    if plan.risks:
        risk_table = Table.grid(expand=True)
        risk_table.add_column("Risks/Warnings", style="yellow")
        for risk in plan.risks:
            risk_table.add_row(risk)
        console.print(Panel(risk_table, title="⚠️  Alerts", border_style="yellow"))

    console.print("\n[bold dim]Plan ready. Customize SQL & test in staging![/bold dim]")
