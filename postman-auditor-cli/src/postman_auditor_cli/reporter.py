import json
from typing import List, TextIO, Dict
from collections import Counter

import rich.console
import rich.table
from rich import box

from .issues import Issue


class Reporter:
    @staticmethod
    def severity_order(issue: Issue) -> int:
        return {"error": 3, "warning": 2, "info": 1}[issue.severity]

    @classmethod
    def table_report(cls, issues: List[Issue], file: Optional[TextIO] = None) -> None:
        console = rich.console.Console(file=file)
        counts = Counter(issue.severity for issue in issues)
        table = rich.table.Table(box=box.ROUNDED, title="[bold]Postman Audit Report[/bold]", title_style="bold blue")
        table.add_column("Severity", style="bold", no_wrap=True)
        table.add_column("Code")
        table.add_column("Path")
        table.add_column("Message")
        table.add_column("Suggestion", max_width=30)
        for issue in sorted(issues, key=cls.severity_order, reverse=True):
            path_str = "/".join(issue.path)
            table.add_row(
                issue.severity.upper(),
                issue.code,
                path_str,
                issue.message,
                issue.suggestion or "",
            )
        console.print(table)
        summary = f"Errors: {counts['error']} | Warnings: {counts['warning']} | Info: {counts['info']}"
        console.print(f"\n[bold]{summary}[/bold]")

    @classmethod
    def json_report(cls, issues: List[Issue], file: Optional[TextIO] = None) -> None:
        counts = Counter(issue.severity for issue in issues)
        data: Dict = {
            "summary": dict(counts),
            "issues": [{
                "severity": i.severity,
                "code": i.code,
                "message": i.message,
                "path": i.path,
                "suggestion": i.suggestion,
            } for i in issues],
        }
        json.dump(data, file or console.stdout, indent=2)

    @classmethod
    def report(cls, issues: List[Issue], fmt: str, output: Optional[TextIO] = None) -> None:
        if fmt == "table":
            cls.table_report(issues, output)
        elif fmt == "json":
            cls.json_report(issues, output)
        else:
            raise ValueError(f"Unknown format: {fmt}")
