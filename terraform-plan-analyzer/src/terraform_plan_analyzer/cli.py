import typer
from pathlib import Path
from rich.console import Console
from rich_click import RichClickGroup

from terraform_plan_analyzer.parser import parse_plan_file, get_resource_changes
from terraform_plan_analyzer.summarizer import summarize_changes, format_summary
from terraform_plan_analyzer.table import build_change_table
from terraform_plan_analyzer.risks import assess_risks, format_risks
from terraform_plan_analyzer.export import export_report


app = typer.Typer(add_completion=False, pretty_exceptions_enable=False, cls=RichClickGroup)
console = Console()


@app.command()
def summary(plan_file: Path = typer.Argument(..., exists=True, help="Terraform plan JSON")):
    """Generate concise change summary (creates/updates/destroys by type)."""
    plan = parse_plan_file(plan_file)
    changes = get_resource_changes(plan)
    summary_data = summarize_changes(changes)
    console.print(format_summary(summary_data))


@app.command()
def table(plan_file: Path = typer.Argument(..., exists=True)):
    """Display rich table of all resource changes with highlights."""
    plan = parse_plan_file(plan_file)
    changes = get_resource_changes(plan)
    console.print(build_change_table(changes))


@app.command()
def risks(
    plan_file: Path = typer.Argument(..., exists=True),
    threshold: int = typer.Option(0, "--threshold", "-t", help="Alert if risks >= threshold"),
):
    """Assess and list potential risks (deletes, exposures, etc.)."""
    plan = parse_plan_file(plan_file)
    changes = get_resource_changes(plan)
    risks_list = assess_risks(changes)
    if len(risks_list) >= threshold:
        console.print(format_risks(risks_list))
    else:
        console.print("✅ No significant risks detected.")


@app.command()
def export(
    plan_file: Path = typer.Argument(..., exists=True),
    output: Path = typer.Argument("report.md", help="Output file"),
    fmt: str = typer.Option("md", "--format", "-f", help="Format: md|html"),
):
    """Export full report (summary + table + risks) to Markdown/HTML."""
    plan = parse_plan_file(plan_file)
    changes = get_resource_changes(plan)
    summary_data = summarize_changes(changes)
    risks_list = assess_risks(changes)
    export_report(output, summary_data, changes, risks_list, fmt)
    console.print(f"📄 Report exported to {output}")


def main():
    if __name__ == "__main__":
        app()
