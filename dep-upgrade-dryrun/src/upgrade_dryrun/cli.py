import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, MofNCompleteColumn
from pathlib import Path
import tempfile
import shutil
import subprocess
import json
from typing import List, Dict, Any, Optional, Tuple

from .ecosystems import ecosystems, Ecosystem
from .parsers import parse_npm_lock, parse_poetry_lock, parse_cargo_lock
from .utils import bump_type

app = typer.Typer(add_completion=False)
console = Console()

@app.command()
def scan(
    directory: Path = typer.Argument(Path("."), exists=True, file_okay=False),
    ecosystems_str: str = typer.Option("all", "--ecosystems"),
    json_output: bool = typer.Option(False, "--json"),
):
    """Scan directory for workspaces and simulate dependency upgrades."""
    if ecosystems_str == "all":
        ecos_list: List[Ecosystem] = list(ecosystems.values())
    else:
        ecos_list = [ecosystems[name] for name in ecosystems_str.split(",") if name in ecosystems]

    workspaces = find_workspaces(directory, ecos_list)
    if not workspaces:
        typer.echo("No supported workspaces found.", err=True)
        raise typer.Exit(1)

    results = []
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        MofNCompleteColumn(),
        console=console,
    ) as progress:
        task_id = progress.add_task("Scanning...", total=len(workspaces))
        for eco, ws_path in workspaces:
            try:
                result = simulate_update(eco, ws_path)
                results.append(result)
            except Exception as e:
                console.print(f"[red]Error in {ws_path.name} ({eco.name}): {str(e)}[/]")
                result = {"path": str(ws_path), "ecosystem": eco.name, "error": str(e)}
                results.append(result)
            progress.advance(task_id)

    if json_output:
        console.print(json.dumps(results, indent=2))
    else:
        for result in results:
            print_result(result, console)

@app.command()
def run(
    directory: Path = typer.Argument(..., exists=True, file_okay=False),
    ecosystem_name: str = typer.Argument(...,),
):
    """Run simulation on a single workspace."""
    if ecosystem_name not in ecosystems:
        typer.echo(f"Unknown ecosystem: {ecosystem_name}", err=True)
        raise typer.Exit(1)
    eco = ecosystems[ecosystem_name]
    if not all((directory / f).exists() for f in eco.required_files):
        typer.echo(f"Missing files for {ecosystem_name}: {eco.required_files}", err=True)
        raise typer.Exit(1)
    result = simulate_update(eco, directory)
    print_result(result, console)

def main():
    app()

if __name__ == "__main__":
    main()

# Helper functions
def find_workspaces(root: Path, ecos: List[Ecosystem]) -> List[Tuple[Ecosystem, Path]]:
    workspaces = []
    visited = set()
    for eco in ecos:
        for candidate in root.rglob("*"):
            if candidate.is_dir():
                ws_tuple = (tuple(eco.required_files), str(candidate))
                if ws_tuple not in visited and all((candidate / f).exists() for f in eco.required_files):
                    visited.add(ws_tuple)
                    workspaces.append((eco, candidate))
    return workspaces

def simulate_update(eco: Ecosystem, ws_path: Path) -> Dict[str, Any]:
    with tempfile.TemporaryDirectory() as tmp_dir:
        temp_path = Path(tmp_dir)
        for fname in eco.required_files:
            shutil.copy2(ws_path / fname, temp_path / fname)
        lock_path = temp_path / eco.lockfile
        old_content = lock_path.read_text(encoding="utf-8")
        old_deps, old_total, old_sizes = eco.parse_lock(lock_path)

        proc = subprocess.run(
            eco.update_cmd,
            cwd=temp_path,
            capture_output=True,
            text=True,
            timeout=30,
        )
        if proc.returncode != 0:
            raise RuntimeError(f"Update command failed:\n{proc.stderr}")

        new_content = lock_path.read_text(encoding="utf-8")
        if old_content == new_content:
            return {
                "path": str(ws_path),
                "ecosystem": eco.name,
                "up_to_date": True,
            }

        new_deps, new_total, new_sizes = eco.parse_lock(lock_path)

    # Compute changes
    all_names = set(old_deps) | set(new_deps)
    changes = []
    for name in sorted(all_names):
        old_ver = old_deps.get(name)
        new_ver = new_deps.get(name)
        if old_ver is None:
            typ = "added"
            delta_size = new_sizes.get(name, 0) if new_sizes else 0
        elif new_ver is None:
            typ = "removed"
            delta_size = -(old_sizes.get(name, 0) if old_sizes else 0)
        else:
            typ = bump_type(old_ver, new_ver)
            delta_size = (
                (new_sizes.get(name, 0) if new_sizes else 0)
                - (old_sizes.get(name, 0) if old_sizes else 0)
            )
        changes.append({"name": name, "old": old_ver, "new": new_ver, "type": typ, "delta_size": delta_size})

    total_delta = (new_total or 0) - (old_total or 0)
    return {
        "path": str(ws_path),
        "ecosystem": eco.name,
        "up_to_date": False,
        "changes": changes,
        "total_size_delta": total_delta,
        "old_total_size": old_total,
        "new_total_size": new_total,
    }

def print_result(result: Dict[str, Any], console: Console):
    path = result["path"]
    eco = result["ecosystem"]
    if result.get("up_to_date"):
        console.print(f"[green]✓ {path} ({eco}): up to date[/]")
        return
    if "error" in result:
        console.print(f"[red]✗ {path} ({eco}): {result['error']}[/]" )
        return

    table = Table(title=f"{Path(path).name} ({eco}) {Path(path).parent}")
    table.add_column("Package", style="cyan")
    table.add_column("Old")
    table.add_column("New")
    table.add_column("Type")
    table.add_column("Δ Size (KB)")

    total_delta_kb = result["total_size_delta"] / 1024.0 if result["total_size_delta"] else 0
    for ch in result["changes"]:
        old = ch["old"] or "-"
        new = ch["new"] or "-"
        typ = ch["type"]
        delta_kb = ch["delta_size"] / 1024.0
        color_map = {
            "major": "red",
            "minor": "yellow",
            "patch": "green",
            "added": "bright_green",
            "removed": "bright_red",
            "unknown": "white",
        }
        style = f"[{color_map.get(typ, 'white')]bold[/]"
        table.add_row(ch["name"], old, new, f"[{style}]{typ}[/{style}]", f"{delta_kb:+.1f}")

    caption = "No size info"
    if result["old_total_size"] is not None:
        old_kb = result["old_total_size"] / 1024
        new_kb = result["new_total_size"] / 1024
        caption = f"Total: {old_kb:.1f}KB → {new_kb:.1f}KB (Δ {total_delta_kb:+.1f}KB)"
    table.caption = caption

    console.print(table)
