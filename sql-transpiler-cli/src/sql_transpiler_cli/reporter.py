import difflib
import json
from pathlib import Path
from typing import Any, Dict, List

from rich.console import Console
from rich.table import Table
from rich import print as rprint

from .types import Issue


console = Console()


def pretty_diff(original: str, new: str) -> str:
    """Generate unified diff as string."""
    diff_lines = difflib.unified_diff(
        original.splitlines(keepends=True),
        new.splitlines(keepends=True),
        fromfile="original",
        tofile="transpiled",
        lineterm="",
    )
    return "".join(diff_lines)


def report_summary(
    results: List[Dict[str, Any]],
    dry_run: bool,
    output: Path | None,
    in_place: bool,
    json_out: bool,
    base_path: Path,
) -> None:
    """Print summary table and diffs/outputs."""

    if json_out:
        print(json.dumps({"results": results}, indent=2))
        return

    total = len(results)
    success = sum(1 for r in results if r["success"])
    changed = sum(1 for r in results if r.get("changed", False))

    table = Table(title="SQL Transpilation Summary")
    table.add_column("File", style="cyan", no_wrap=True)
    table.add_column("Status")
    table.add_column("Changed")
    table.add_column("Issues")

    for res in results:
        status = "✅" if res["success"] else "❌ " + (res.get("error") or ", ".join(i.message for i in res.get("issues", []))[:50])
        ch = "🔄" if res.get("changed") else "—"
        issues_cnt = len(res.get("issues", []))
        table.add_row(res["file"], status, ch, str(issues_cnt))

    console.print(table)
    console.print(f"\n[bold]Summary:[/bold] {success}/{total} successful, {changed} changed.")

    # D diffs if dry-run or no output
    if dry_run or (not output and not in_place):
        for res in results:
            if res.get("changed"):
                console.print(f"\n[bold cyan]{res['file']}[/bold cyan]")
                diff = pretty_diff(res["original"], res["transpiled"])
                console.print("[dim]" + diff + "[/dim]")

    # Write outputs
    if output:
        output.mkdir(parents=True, exist_ok=True)
        for res in results:
            fpath = Path(res["file"])
            rel_path = fpath.relative_to(base_path)
            out_path = output / rel_path
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(res["transpiled"])
        rprint(f"[green]Wrote {len(results)} files to {output}[/]\n")

    if in_place:
        updated = 0
        for res in results:
            if res.get("changed"):
                Path(res["file"]).write_text(res["transpiled"])
                updated += 1
        rprint(f"[green]Updated {updated} files in-place.[/]")