import json
import sys
from pathlib import Path
from typing import Annotated, List, Optional
import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table
from rich import print as rprint

from .extractor import fetch_metadata
from .models import Metadata


app = typer.Typer(no_args_is_help=True, add_completion=False)
console = Console()


@app.command()
def cli(
    urls: Annotated[
        List[str],
        typer.Argument(
            ...,
            min_length=1,
            help="One or more URLs (space-separated). Use `xargs` for batch files.",
        ),
    ],
    json_output: bool = typer.Option(False, "--json/-j", help="JSON output."),
    user_agent: Optional[str] = typer.Option(None, "--user-agent/-u"),
    timeout: int = typer.Option(10, "--timeout/-t", min=1, max=300),
    cache_dir: str = typer.Option(
        "~/.cache/link-metadata-cli", "--cache-dir"
    ),
    cache_expire: int = typer.Option(3600, "--cache-expire"),
    no_cache: bool = typer.Option(False, "--no-cache"),
):
    """Extract rich metadata from URLs."""

    results: List[dict] = []

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        console=console,
        transient=True,
    ) as progress:
        task = progress.add_task("[cyan]Fetching metadata...", total=len(urls))
        for url in urls:
            try:
                meta = fetch_metadata(
                    url,
                    user_agent=user_agent,
                    timeout=timeout,
                    cache_dir=cache_dir,
                    cache_expire=cache_expire,
                    use_cache=not no_cache,
                )
                results.append(meta.model_dump(mode="json"))
            except Exception as e:
                results.append({"url": url, "error": str(e)})
            progress.advance(task)

    if json_output:
        print(json.dumps(results, indent=2))
    else:
        table = Table(title="Link Metadata", show_header=True, box="heavy")
        table.add_column("URL", style="cyan", no_wrap=True)
        table.add_column("Title", style="magenta", ratio=1)
        table.add_column("Description", style="green")
        table.add_column("Image", style="yellow")
        table.add_column("Site", style="blue")
        table.add_column("Type", style="white")

        for res in results:
            if "error" in res:
                table.add_row(res["url"], "", res["error"], "", "", "")
            else:
                title = (
                    res.get("title", "")[:40] + "..."
                    if len(res.get("title", "")) > 40
                    else res.get("title", "")
                )
                desc = (
                    res.get("description", "")[:50] + "..."
                    if res.get("description", "")
                    else ""
                )
                table.add_row(
                    res["url'],
                    title,
                    desc,
                    res.get("image", ""),
                    res.get("site_name", ""),
                    res.get("type", ""),
                )
        console.print(table)


if __name__ == "__main__":
    app()
