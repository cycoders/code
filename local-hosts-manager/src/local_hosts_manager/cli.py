import typer
from rich.console import Console
from .hosts import HostsManager, __version__

app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
console = Console()

@app.command(help="List all host entries")
def list_():
    """Display hosts table."""
    try:
        hm = HostsManager()
        hm.load()
        hm.list()
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

@app.command(help="Add IP → domain(s)")
def add(
    ip: str = typer.Argument(..., help="IP address"),
    domains: List[str] = typer.Argument(..., help="Domain(s)"),
    comment: Optional[str] = typer.Option(None, "--comment", help="Optional comment"),
    force: bool = typer.Option(False, "--force", help="Ignore conflicts"),
):
    """Add or update host mapping."""
    try:
        hm = HostsManager()
        hm.load()
        hm.add(ip, domains, comment, force)
        hm.save()
        console.print(f"[green]Added: {ip} → {', '.join(domains)}[/green]")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

@app.command(help="Remove domain(s)")
def remove(domains: List[str] = typer.Argument(..., help="Domain(s)")):
    """Remove domains from all entries."""
    try:
        hm = HostsManager()
        hm.load()
        hm.remove(domains)
        hm.save()
        console.print("[green]Removed.[/green]")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

@app.command(help="Show stats")
def stats():
    """Display statistics."""
    try:
        hm = HostsManager()
        hm.load()
        s = hm.stats()
        console.print(
            f"[bold]Stats:[/bold] {s['entries']} entries, {s['domains']} domains, "
            f"{s['local']} local | "
            f"Duplicates: {len(s['duplicates'])}"
        )
        if s['duplicates']:
            console.print(f"[red]{', '.join(s['duplicates'])}[/red]")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

@app.command(help="Search domains")
def search(pattern: str = typer.Argument(..., help="Search pattern")):
    """Search domains case-insensitive."""
    try:
        hm = HostsManager()
        hm.load()
        hm.search(pattern)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

@app.command(help="Validate entries")
def validate():
    """Check for duplicates/invalid."""
    try:
        hm = HostsManager()
        hm.load()
        errors = hm.validate()
        if errors:
            console.print("[red]Issues:[/red]")
            for err in errors:
                console.print(f"  {err}")
        else:
            console.print("[green]✓ All valid.[/green]")
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

@app.command(help="List backups")
def backups():
    """List available backups."""
    try:
        hm = HostsManager()
        hm.list_backups()
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

@app.command(help="Restore backup")
def restore(filename: str = typer.Argument(..., help="Backup filename")):
    """Restore from backup."""
    try:
        hm = HostsManager()
        hm.restore(filename)
    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1)

@app.callback(invoke_without_command=True)
def main(
    version: bool = typer.Option(None, "--version", callback=lambda v: console.print(f"local-hosts-manager {__version__}") or typer.Exit(), help="Show version"),
):
    """Safely manage /etc/hosts for dev.\n\nRun with sudo/admin if editing."""
    if version:
        raise typer.Exit()