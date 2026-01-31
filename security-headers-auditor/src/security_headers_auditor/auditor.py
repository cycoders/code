from typing import Dict, Any
import json
import statistics
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich import box

from .scanner import WebScanner
from .header_checks import check_security_headers
from .types import HeaderCheck


class Auditor:
    """Core auditing logic."""

    def __init__(self, timeout: int = 10, user_agent: str | None = None):
        self.scanner = WebScanner(timeout=timeout, user_agent=user_agent)
        self.console = Console()

    def audit(self, url: str, output_json: bool = False) -> None:
        """Run full audit."""
        data = self.scanner.scan(url, fetch_html=False)
        checks = check_security_headers(data['headers'])
        scores = [c.score for c in checks.values()]
        avg_score = statistics.mean(scores)
        grade = self._compute_grade(avg_score)

        report = {
            'url': data['url'],
            'status_code': data['status_code'],
            'grade': grade,
            'score': round(avg_score, 1),
            'headers': {k: c.dict() for k, c in checks.items()},
        }

        if output_json:
            print(json.dumps(report, indent=2))
            return

        self._render_report(report, checks)

    def _compute_grade(self, score: float) -> str:
        if score >= 8.0:
            return 'A'
        elif score >= 6.0:
            return 'B'
        elif score >= 4.0:
            return 'C'
        elif score >= 2.0:
            return 'D'
        return 'F'

    def _render_report(self, report: Dict[str, Any], checks: Dict[str, HeaderCheck]) -> None:
        self.console.print(Panel(
            f"[bold green]Grade: {report['grade']} ({report['score']:.1f}/10)[/]",
            title="[bold]Security Score[/]",
            border_style="green",
        ))

        table = Table(box=box.ROUNDED, title="Security Headers")
        table.add_column("Header", style="cyan")
        table.add_column("Status", justify="center")
        table.add_column("Score", justify="center")
        table.add_column("Recommendation", max_width=40)

        missing = []
        for name, check in checks.items():
            status_color = {
                HeaderStatus.PRESENT: "green",
                HeaderStatus.MISSING: "red",
                HeaderStatus.INVALID: "yellow",
            }[check.status]
            table.add_row(
                name.replace('-', ' ').title(),
                f"[{status_color}]{check.status.title()}[/]",
                str(check.score),
                check.recommendation,
            )
            if check.status == HeaderStatus.MISSING:
                missing.append(name)

        self.console.print(table)

        if missing:
            self.console.print(f"\n[bold red]⚠️  Missing ({len(missing)}):[/] {', '.join(h.replace('-',' ').title() for h in missing)}")
