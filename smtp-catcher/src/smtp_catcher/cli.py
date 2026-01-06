import typer
from pathlib import Path
from typing import Optional
import rich_click as click
from rich.console import Console
from rich import box
from rich.panel import Panel
from rich.table import Table

from .server import start_server
from .storage import init_db, list_email_summaries, get_email, delete_email, clear_emails

app = typer.Typer(click=click, add_completion=False)
console = Console()

@app.command(help="Start the SMTP capture server")
def start(
    host: str = typer.Option("127.0.0.1", "--host", envvar="SMTP_CATCHER_HOST"),
    port: int = typer.Option(1025, "--port", envvar="SMTP_CATCHER_PORT"),
    data_dir: Path = typer.Option(Path(".smtp_catcher"), "--data-dir", envvar="SMTP_CATCHER_DATA_DIR"),
):
    """Start the SMTP server. Blocks until Ctrl+C."""
    data_dir.mkdir(parents=True, exist_ok=True)
    init_db(data_dir)
    console.print(f"[bold green]SMTP Catcher starting[/] on {host}:{port}, data: {data_dir.absolute()}")
    try:
        start_server(host, port, data_dir)
    except KeyboardInterrupt:
        console.print("[yellow]Shutting down...[/]")
    except Exception as e:
        console.print(f"[red]Error: {e}[/]")
        raise typer.Exit(code=1)

@app.command(help="List captured emails")
def list_emails(
    data_dir: Path = typer.Option(Path(".smtp_catcher"), "--data-dir", envvar="SMTP_CATCHER_DATA_DIR"),
    limit: int = typer.Option(10, "--limit"),
    sender: Optional[str] = typer.Option(None, "--sender"),
):
    """List recent emails (most recent first)."""
    summaries = list_email_summaries(data_dir, limit=limit, sender_filter=sender)
    if not summaries:
        console.print("[yellow]No emails found.[/]")
        return
    table = Table(title="Captured Emails", box=box.ROUNDED)
    table.add_column("ID", style="cyan")
    table.add_column("Received", style="magenta")
    table.add_column("From", style="green")
    table.add_column("# To", justify="right")
    table.add_column("Subject", style="white")
    for s in summaries:
        table.add_row(
            str(s["id"]),
            str(s["received_at"])[:16],
            s["sender"][:40] + "..." if len(s["sender"]) > 40 else s["sender"],
            str(s["recipients_count"]),
            (s["subject"] or "(no subject)")[:50] + "..." if len(s["subject"] or "") > 50 else (s["subject"] or "(no subject)"),
        )
    console.print(table)

@app.command(help="Show email details")
def show(
    id_: int,
    data_dir: Path = typer.Option(Path(".smtp_catcher"), "--data-dir", envvar="SMTP_CATCHER_DATA_DIR"),
    fmt: str = typer.Option("pretty", "--format", choices=["pretty", "json"]),
):
    """View full email."""
    email = get_email(data_dir, id_)
    if not email:
        console.print(f"[red]Email {id_} not found.[/]")
        raise typer.Exit(code=1)
    if fmt == "json":
        from json import dumps
        console.print_json(data=email)
    else:
        # Headers table
        headers_table = Table("Header", "Value", box=box.MINIMAL, title="Headers", show_header=True)
        for k, v in sorted(email["headers"].items()):
            headers_table.add_row(k, str(v)[:100] + "..." if len(str(v)) > 100 else str(v))
        console.print(headers_table)
        # Body
        body = email.get("body_html") or email.get("body_text", "(no body)")
        console.print(Panel(body, title=f"From: {email['sender']} | To: {len(email['recipients'])} | Subject: {email['subject'] or '(no subject)'}", box=box.ROUNDED))

@app.command(help="Delete an email")
def delete(
    id_: int,
    data_dir: Path = typer.Option(Path(".smtp_catcher"), "--data-dir", envvar="SMTP_CATCHER_DATA_DIR"),
    yes: bool = typer.Option(False, "--yes"),
):
    """Delete email by ID."""
    if not yes:
        console.print("[yellow]Use --yes to confirm.[/]")
        raise typer.Exit(code=1)
    deleted = delete_email(data_dir, id_)
    if deleted:
        console.print(f"[green]Deleted email {id_}[/]")
    else:
        console.print(f"[red]Email {id_} not found.[/]")
        raise typer.Exit(code=1)

@app.command(help="Clear all emails")
def clear(
    data_dir: Path = typer.Option(Path(".smtp_catcher"), "--data-dir", envvar="SMTP_CATCHER_DATA_DIR"),
    yes: bool = typer.Option(False, "--yes"),
):
    """Delete all emails."""
    if not yes:
        console.print("[yellow]Use --yes to confirm.[/]")
        raise typer.Exit(code=1)
    clear_emails(data_dir)
    console.print("[green]Cleared all emails.[/]")

if __name__ == "__main__":
    app()