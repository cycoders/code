from rich.console import Console
from rich.table import Table
from rich.json import JSONRenderer
from rich import print as rprint
from typing import Dict, Any, List

console = Console()

json_renderer = JSONRenderer()

def render_result(result: Dict[str, Any]) -> None:
    """Render query/mutation result with data/errors."""
    if "data" in result and result["data"] is not None:
        console.print("[bold green]Data:[/bold green]")
        console.print_json(data=result["data"], indent=2, expand_all=True)
    
    if "errors" in result and result["errors"]:
        console.print("[bold red]Errors:[/bold red]")
        for error in result["errors"]:
            console.print(f"  [red]{error.get('message', 'Unknown error')}[/red]")
            if "locations" in error:
                console.print(f"    Location: {error['locations']}")
            if "path" in error:
                console.print(f"    Path: {error['path']}")
    
    if "extensions" in result:
        console.print("[dim]Extensions:[/dim]")
        console.print_json(data=result["extensions"], indent=2)

def render_subscription_event(event: Dict[str, Any]) -> None:
    """Render single subscription event."""
    console.print("[bold blue]Event:[/bold blue]")
    console.print_json(data=event, indent=2, expand_all=True)

def render_history_list(history: List[Dict[str, Any]]) -> None:
    """Render history table."""
    table = Table(title="Recent Queries", show_header=True, header_style="bold magenta")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Endpoint", max_width=40)
    table.add_column("Query Preview", max_width=50)
    table.add_column("Timestamp", style="green")
    
    for item in history:
        table.add_row(
            str(item["id"]),
            str(item["endpoint"]),
            str(item["query"]),
            str(item["timestamp"]),
        )
    console.print(table)

def render_schema(schema_data: Dict[str, Any]) -> None:
    """Render introspected schema."""
    console.print("[bold cyan]GraphQL Schema[/bold cyan]")
    console.print_json(data=schema_data, indent=2, expand_all=True)
