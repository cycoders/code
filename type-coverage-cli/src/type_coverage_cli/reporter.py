import json
from typing import TextIO

from rich.table import Table
from rich.console import Console, ConsoleRenderable
from rich.text import Text

from .models import OverallStats


def print_table_report(stats: OverallStats, console: Console) -> None:
    # Overall summary
    summary_table = Table(title="[bold cyan]Type Coverage Summary[/bold cyan]", show_header=True, header_style="bold magenta")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Coverage", justify="right")
    summary_table.add_column("Details", justify="right")

    summary_table.add_row(
        "Functions",
        f"{stats.func_coverage():.1f}%",
        f"{stats.funcs.typed}/{stats.funcs.total}",
    )
    summary_table.add_row(
        "Parameters",
        f"{stats.param_coverage():.1f}%",
        f"{stats.params.typed}/{stats.params.total}",
    )
    summary_table.add_row(
        "Returns",
        f"{stats.return_coverage():.1f}%",
        f"{stats.returns.typed}/{stats.returns.total}",
    )
    summary_table.add_row("Files", str(stats.files), "")

    console.print(summary_table)

    if stats.file_stats:
        # Per-file details
        detail_table = Table(title="[bold cyan]Per-File Breakdown[/bold cyan]", show_header=True, header_style="bold magenta")
        detail_table.add_column("File", style="green")
        detail_table.add_column("Funcs %", justify="right")
        detail_table.add_column("Params %", justify="right")
        detail_table.add_column("Returns %", justify="right")
        detail_table.add_column("Params cnt", justify="right")
        detail_table.add_column("Returns cnt", justify="right")

        for fs in sorted(stats.file_stats, key=lambda f: f.funcs.percentage):
            detail_table.add_row(
                fs.path,
                f"{fs.funcs.percentage:.1f}%",
                f"{fs.params.percentage:.1f}%",
                f"{fs.returns.percentage:.1f}%",
                f"{fs.params.typed}/{fs.params.total}",
                f"{fs.returns.typed}/{fs.returns.total}",
            )
        console.print(detail_table)


def print_json_report(stats: OverallStats, output: TextIO) -> None:
    from .models import asdict
    json.dump(stats.to_dict(), output, indent=2)
    output.write("\n")
