from pathlib import Path
from typing import Any

import rich.console
import rich.tree
from rich import box
from rich.panel
from rich.table
from rich.console import Console
from rich.markdown

from x509_chain_checker.models import ChainReport, CertValidation


def report(output: str, report: ChainReport, file: Path | None = None) -> None:
    content = _generate_content(report)
    if file:
        with open(file, "w") as f:
            f.write(content)
    else:
        print(content)


def _rich_report(console: Console, report: ChainReport) -> None:
    tree = rich.tree.Tree("🌳 Certificate Chain", guide_style="cyan")
    for cert in report.chain:
        emoji = {"valid": "✅", "warning": "⚠️", "invalid": "❌", "unknown": "❓"}[cert.status]
        label = f"{emoji} [bold]{cert.subject_cn}[/bold] (serial: {cert.serial[:16]}...)"
        node = tree.add(label)
        if cert.issues:
            node.add(f"[red]Issues:[/red] {', '.join(iss.value for iss in cert.issues)}")
        node.add(f"Valid: {cert.not_before.strftime('%Y-%m-%d')} → {cert.not_after.strftime('%Y-%m-%d')}")
        node.add(f"FP: {cert.fingerprint_sha256[:32]}...")
    console.print(tree)
    status_emoji = {"valid": "✅", "warning": "⚠️", "invalid": "❌"}[report.overall_status]
    console.print(f"\n{status_emoji} Overall: [bold]{report.overall_status.upper()}[/bold] | {report.summary}")


def _json_report(report: ChainReport) -> str:
    return report.model_dump_json(indent=2)


def _html_report(console: rich.console.Console, report: ChainReport) -> str:
    console.record = True
    _rich_report(console, report)
    console.record = False
    return console.export_html(
        title="X509 Chain Report",
        stylesheet=("body { font-family: monospace; } .tree { margin: 1em 0; }"),
    )


def _generate_content(report: ChainReport) -> str:
    console = Console(record=True, force_terminal=True)
    if output := "rich":  # Default
        _rich_report(console, report)
        return console.export_text()
    elif output == "json":
        return _json_report(report)
    elif output == "html":
        return _html_report(console, report)
    raise ValueError(f"Unknown output: {output}")