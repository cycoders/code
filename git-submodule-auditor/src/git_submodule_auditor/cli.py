import typer
import subprocess
from rich.console import Console
from rich.markdown import Markdown
from .auditor import Auditor
from .models import submodules_to_dict


app = typer.Typer(add_completion=False)
console = Console()


@app.command()
def list_():
    """List submodules with rich status table."""
    auditor = Auditor()
    auditor.print_list(console)


@app.command()
def audit(
    json_output: bool = typer.Option(False, "--json", help="Output JSON for CI/automation")
):
    """Comprehensive audit with issues and cycles."""
    auditor = Auditor()
    auditor.print_audit(console)
    if json_output:
        data = {
            "submodules": submodules_to_dict(auditor.submodules),
            "cycles": auditor.cycles,
            "summary": {
                "total": len(auditor.submodules),
                "risky": len([s for s in auditor.submodules if s.issues]),
            }
        }
        console.print_json(data=data, indent=2)


@app.command()
def graph():
    """Generate Mermaid diagram for submodule deps (copy-paste friendly)."""
    auditor = Auditor()
    mermaid = auditor.generate_mermaid()
    md = Markdown(f"```mermaid\n{mermaid}\n```")
    console.print(md)


@app.command()
def update(
    dry_run: bool = typer.Option(True, "--dry-run", help="Show commands only"),
):
    """Safely update outdated submodules (gates on cycles/dirty)."""
    auditor = Auditor()
    if auditor.cycles:
        console.print("[bold red]Aborted: Cycles detected. Fix first.[/bold red]")
        raise typer.Exit(code=1)
    updated = 0
    for sub in auditor.submodules:
        if sub.outdated and not sub.is_dirty:
            cmd = f"git submodule update --remote {sub.path}"
            console.print(f"[green]↻ {sub.path} ← {sub.current_commit[:8]} [bold](safe)[/bold]")
            if not dry_run:
                try:
                    subprocess.run(cmd.split(), cwd=auditor.repo_path, check=True, capture_output=True)
                    updated += 1
                except subprocess.CalledProcessError:
                    console.print("[red]Failed![/red]")
        elif sub.is_dirty:
            console.print(f"[yellow]⏸️  {sub.path}: dirty (commit first)[/yellow]")
        else:
            console.print(f"[green]✅ {sub.path}: up-to-date[/green]")
    if dry_run:
        console.print(f"[blue]Dry-run OK. Use --execute to apply.[/blue]")
    else:
        console.print(f"[green]Updated {updated}/{len(auditor.submodules)} modules.[/green]")


def main():
    app(prog_name="git-submodule-auditor")


if __name__ == "__main__":
    main()
