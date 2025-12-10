import typer
from pathlib import Path
from rich.console import Console
from rich.markdown import Markdown

from . import __version__
from .config import load_config
from .parser import parse_commits, NoConventionalCommits, ParserError
from .renderer import Renderer


app = typer.Typer()
console = Console()


@app.command(help="Generate changelog from conventional commits")
def generate(
    repo: Path = typer.Argument(Path("."), exists=True, help="Git repository path"),
    since: str = typer.Option("v1.0.0", "--since/-s", help="Git ref range start (e.g. v1.0.0)"),
    until: str = typer.Option("HEAD", "--until/-u", help="Git ref range end"),
    output: Path = typer.Option("CHANGELOG.md", "--output/-o", file_okay=True, writable=True),
    config: Path = typer.Option(None, "--config/-c"),
    preview: bool = typer.Option(False, "--preview/-p"),
):
    """Generate and optionally preview changelog."""
    try:
        cfg = load_config(config)
        commits = parse_commits(str(repo), since, until)

        changelog_md = Renderer.render(commits, cfg)

        if preview:
            md = Markdown(changelog_md)
            console.print(md)
            return

        if output.exists():
            with open(output, "r", encoding="utf-8") as f:
                existing = f.read()
            content = changelog_md + "\n" + existing
        else:
            content = changelog_md

        with open(output, "w", encoding="utf-8") as f:
            f.write(content)

        console.print(f"[green]✨ Changelog generated: {output}[/]")

    except NoConventionalCommits as exc:
        console.print(f"[yellow]⚠️  {exc}[/]\n[grey]Use conventional commits like 'feat: add x'.[/]")
        raise typer.Exit(1) from None
    except ParserError as exc:
        console.print(f"[red]❌ Parse error: {exc}[/]")
        raise typer.Exit(1) from None
    except Exception as exc:
        console.print(f"[red]💥 Unexpected error: {exc}[/]")
        console.print_exception(show_locals=True)
        raise typer.Exit(1) from None


@app.command(help="Show config template")
def config():
    """Print default config template."""
    import yaml
    from .config import DEFAULT_CONFIG

    print("# .auto-changelog.yaml")
    print(yaml.dump(DEFAULT_CONFIG, default_flow_style=False, sort_keys=False))


@app.callback()
def main(version: bool = typer.Option(False, "--version", help="Show version")):
    """Auto-Changelog CLI."""
    if version:
        console.print(f"auto-changelog [bold cyan]v{__version__}[/]")
        raise typer.Exit()


if __name__ == "__main__":
    app()