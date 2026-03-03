from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box

from .models import AuditReport

console = Console()

def render_console(report: AuditReport):
    # Score panel
    score_emoji = "✅" if report.passed else "❌"
    console.print(
        Panel(
            f"[bold]{score_emoji} Score: {report.score:.1f}% ({sum(c.passed for c in report.checks)}/{len(report.checks)} checks)[/bold]",
            title=f"CORS Audit: {report.url}",
            border_style="green" if report.passed else "red",
        )
    )

    # Summary table
    table = Table(title="Summary", box=box.ROUNDED)
    table.add_column("Origin", style="cyan")
    table.add_column("Simple", justify="center")
    table.add_column("Preflight", justify="center")
    table.add_column("Creds OK", justify="center")

    for tc in report.test_cases:
        simple_emoji = "🟢" if tc.simple_request.passed else "🔴"
        pre_emoji = "🟢" if tc.preflight_request.passed else "🔴"
        creds_ok = "🟢" if not report.config.credentials or all(h.get("access-control-allow-credentials") == "true" for h in [tc.simple_request, tc.preflight_request]) else "🔴"
        table.add_row(
            tc.origin[:30] + "..." if len(tc.origin) > 30 else tc.origin,
            simple_emoji,
            pre_emoji,
            creds_ok,
        )
    console.print(table)

    # Details panels
    for check in report.checks:
        status_style = "green" if check.passed else "red"
        details_panel = Panel(
            "\n".join(f"• {d}" for d in check.details),
            title=f"{check.type.title()} ({check.origin}) [{status_style}]{check.status_code}[/{status_style}]",
            border_style=status_style,
        )
        console.print(details_panel)

    if report.recommendations:
        rec_panel = Panel("\n".join(f"➤ {r}" for r in report.recommendations), title="Recommendations", border_style="yellow")
        console.print(rec_panel)

    console.print(f"\n[bold blue]Full headers saved in JSON mode.[/]")

def render_json(report: AuditReport):
    print(report.model_dump_json(indent=2, exclude_none=True))