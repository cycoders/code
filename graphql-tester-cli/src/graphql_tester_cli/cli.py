import typer
import json
import asyncio
from typing import Optional
from rich.prompt import Prompt, Confirm
from rich.console import Console

from .client import GraphQLClient, INTROSPECTION_QUERY
from .ui import console, render_result, render_subscription_event, render_history_list, render_schema
from .history import HistoryManager

app = typer.Typer(add_completion=False, no_args_is_help=True)
history_mgr = HistoryManager()

@app.command(short_help="Execute GraphQL query/mutation")
def query(
    endpoint: str = typer.Argument(..., help="GraphQL endpoint"),
    document: str = typer.Argument(..., help="GraphQL document"),
    variables: str = typer.Option("{}", "--variables", help="JSON variables"),
    headers: str = typer.Option("{}", "--headers", help="JSON headers"),
) -> None:
    """Execute a GraphQL query or mutation with rich output."""
    try:
        var_dict = json.loads(variables)
        head_dict = json.loads(headers)
    except json.JSONDecodeError as e:
        typer.echo(f"[red]Invalid JSON: {e}", err=True)
        raise typer.Exit(code=1)

    client = GraphQLClient(endpoint, head_dict)
    result = client.execute(document, var_dict)
    render_result(result)
    history_mgr.save(endpoint, document, var_dict, result)

@app.command(short_help="Subscribe to GraphQL events")
def subscription(
    endpoint: str = typer.Argument(..., help="HTTP GraphQL endpoint"),
    ws_endpoint: Optional[str] = typer.Option(None, "--ws-endpoint", help="WS endpoint (auto if unset)"),
    document: str = typer.Argument(..., help="Subscription document"),
    variables: str = typer.Option("{}", "--variables"),
    headers: str = typer.Option("{}", "--headers"),
) -> None:
    """Listen to live GraphQL subscription events."""
    try:
        var_dict = json.loads(variables)
        head_dict = json.loads(headers)
    except json.JSONDecodeError as e:
        typer.echo(f"[red]Invalid JSON: {e}", err=True)
        raise typer.Exit(code=1)

    client = GraphQLClient(endpoint, head_dict, ws_endpoint)

    async def run_sub() -> None:
        try:
            console.print("[yellow]Listening for events... (Ctrl+C to stop)", style="bold")
            async for event in client.subscribe(document, var_dict):
                render_subscription_event(event)
        except asyncio.CancelledError:
            pass
        except Exception as e:
            console.print(f"[red]Subscription error: {e}[/red]")

    try:
        asyncio.run(run_sub())
    except KeyboardInterrupt:
        console.print("\n[green]Stopped.[/green]")

@app.command(short_help="Introspect schema")
def introspect(
    endpoint: str = typer.Argument(..., help="GraphQL endpoint"),
    headers: str = typer.Option("{}", "--headers"),
) -> None:
    """Fetch and display full GraphQL schema."""
    try:
        head_dict = json.loads(headers)
    except json.JSONDecodeError as e:
        typer.echo(f"[red]Invalid JSON: {e}", err=True)
        raise typer.Exit(code=1)

    client = GraphQLClient(endpoint, head_dict)
    result = client.execute(INTROSPECTION_QUERY)
    render_schema(result.get("data", {}).get("__schema", {}))

@app.command(short_help="Interactive shell")
def interactive(
    endpoint: str = typer.Argument(..., help="GraphQL endpoint"),
    headers: str = typer.Option("{}", "--headers"),
) -> None:
    """Interactive GraphQL REPL."""
    try:
        head_dict = json.loads(headers)
    except json.JSONDecodeError as e:
        typer.echo(f"[red]Invalid JSON: {e}", err=True)
        raise typer.Exit(code=1)

    client = GraphQLClient(endpoint, head_dict)
    console.print(f"[bold green]GraphQL Tester REPL - {endpoint}[/bold green]")
    console.print("'[bold dim]exit/quit[/], help[/]' to control.")

    while True:
        document = Prompt.ask("[cyan]Document[/]")
        if document.lower() in ("exit", "quit"):
            break
        if document.lower() == "help":
            console.print("Enter GraphQL query/mutation. Follow with JSON variables.")
            continue

        var_str = Prompt.ask("[cyan]Variables[/]", default="{}")
        try:
            var_dict = json.loads(var_str) if var_str.strip() else {}
        except json.JSONDecodeError:
            console.print("[red]Invalid variables JSON. Skipping.[/red]")
            continue

        result = client.execute(document, var_dict)
        render_result(result)
        history_mgr.save(endpoint, document, var_dict, result)

@app.command(short_help="List history")
def history(
    limit: int = typer.Option(20, "--limit", min=1, max=100),
) -> None:
    """List recent queries from history."""
    items = history_mgr.list_recent(limit)
    if not items:
        console.print("[yellow]No history yet.[/yellow]")
    else:
        render_history_list(items)

@app.command(short_help="Replay history item")
def history_replay(
    query_id: int = typer.Argument(..., help="History ID"),
    endpoint: Optional[str] = typer.Option(None, "--endpoint", help="Override endpoint"),
) -> None:
    """Replay and re-execute a historical query."""
    item = history_mgr.get(query_id)
    if not item:
        typer.echo("[red]Query not found.[/red]")
        raise typer.Exit(code=1)

    exec_endpoint = endpoint or item["endpoint"]
    client = GraphQLClient(exec_endpoint)
    result = client.execute(item["query"], item["variables"])
    render_result(result)
    history_mgr.save(exec_endpoint, item["query"], item["variables"], result)
    console.print(f"[green]Replayed as new entry.[/green]")

def main() -> None:
    """Entry point."""
    app(prog_name="graphql-tester")

if __name__ == "__main__":
    main()
