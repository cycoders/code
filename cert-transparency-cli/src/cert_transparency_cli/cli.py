import typer
from datetime import datetime, date
from typing import Optional

import cert_transparency_cli

from .ct_client import CTClient
from .parser import parse_entries, enrich_with_pem
from .output import print_table, print_stats, output_json, output_csv

app = typer.Typer(
    name="cert-transparency-cli",
    help="Audit domain certificates via Certificate Transparency logs",
    add_completion=False,
)

@app.command(help="Search CT logs for domain certificates")
def search(
    domain: str,
    subdomains: bool = typer.Option(
        False, "--subdomains/-s", help="Include subdomains (%.domain.com)"
    ),
    since: Optional[str] = typer.Option(None, "--since", help="Filter not_before >= YYYY-MM-DD"),
    until: Optional[str] = typer.Option(None, "--until", help="Filter not_after <= YYYY-MM-DD"),
    limit: int = typer.Option(200, "--limit/-l", min=1, max=5000, help="Max entries"),
    fetch_pems: int = typer.Option(
        0, "--fetch-pems", min=0, max=50, help="Fetch/parse top N PEMs (slow)"
    ),
    stats: bool = typer.Option(False, "--stats", help="Show issuer/expiration stats"),
    output: str = typer.Option("table", "--output/-o", choices=["table", "json", "csv"]),
):
    query = f"%.{domain}" if subdomains else domain
    typer.echo(f"[bold cyan]Searching CT logs for:[/bold cyan] {query}")

    client = CTClient()
    raw_entries = client.search(query)
    entries = parse_entries(raw_entries[:limit])

    # Date filters
    now = datetime.now()
    if since:
        since_dt = datetime.strptime(since, "%Y-%m-%d")
        entries = [e for e in entries if e.not_before >= since_dt]
    if until:
        until_dt = datetime.strptime(until, "%Y-%m-%d")
        entries = [e for e in entries if e.not_after <= until_dt]

    # Enrich PEMs
    if fetch_pems > 0:
        typer.echo(f"Fetching/parsing {min(fetch_pems, len(entries))} PEMs...")
        for i in range(min(fetch_pems, len(entries))):
            try:
                pem_text = client.fetch_pem(entries[i].id)
                enrich_with_pem(entries[i], pem_text)
            except Exception as e:
                typer.echo(f"[yellow]Skipped PEM {entries[i].id}: {e}[/yellow]")

    # Output
    if output == "table":
        print_table(entries)
        if stats:
            print_stats(entries)
    elif output == "json":
        output_json(entries)
    elif output == "csv":
        output_csv(entries)

    typer.echo(f"[green]Found {len(entries)} certificates[/green]")

if __name__ == "__main__":
    app()