import asyncio
import os
import tomllib
typing
from typer import Typer, Argument, Option, Exit, run
from rich.console import Console

from . import __version__

from .collector import collect_links
from .auditor import audit_links
from .reporter import report_results
from .settings import Settings


app = Typer(name="link-auditor", add_completion=False)
console = Console()


async def async_check(inputs: List[str], **overrides) -> None:
    settings = Settings()

    # Config file
    config_file: Optional[str] = overrides.pop("config_file", None)
    if config_file and os.path.exists(config_file):
        with open(config_file, "rb") as f:
            cfg = tomllib.load(f)
        settings = Settings(**cfg)

    # Override
    for k, v in overrides.items():
        setattr(settings, k, v)

    links = collect_links(inputs, settings)
    if not links:
        console.print("[bold red]No links found to audit.[/]\n")
        raise Exit(code=1)

    console.print(f"[bold cyan]Found {len(links)} unique links to audit...[/bold cyan]")

    results = await audit_links(links, settings)
    report_results(results, overrides.get("format", "table"), overrides.get("output"), console)


@app.command(help="Audit links")
def check(
    inputs: List[str] = Argument(..., help="Files, dirs, URLs, sitemaps"),
    concurrency: int = Option(50, "--concurrency/-c", min=1, max=200),
    timeout: float = Option(10.0, "--timeout/-t", min=1.0),
    max_retries: int = Option(3, "--max-retries/-r", min=0, max=5),
    follow_redirects: bool = Option(True, "--follow-redirects"),
    fmt: str = Option("table", "--format/-f", help="table|json|csv"),
    output: Optional[str] = Option(None, "--output/-o"),
    ignore: List[str] = Option([], "--ignore/-i"),
    config_file: Optional[str] = Option(None, "--config"),
) -> None:
    """Check for broken links."""
    asyncio.run(
        async_check(
            inputs,
            concurrency=concurrency,
            timeout=timeout,
            max_retries=max_retries,
            follow_redirects=follow_redirects,
            format=fmt,
            output=output,
            ignore_patterns=ignore,
            config_file=config_file,
        )
    )


@app.command()
def version():
    console.print(f"link-auditor v{__version__}")


if __name__ == "__main__":
    app()
