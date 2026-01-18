import typer
from pathlib import Path
from typing import Optional

from rich.console import Console

from .analyzer import get_all_file_sizes, get_used_files
from .parser import parse_copy_patterns
from .reporter import generate_dockerignore, print_report


app = typer.Typer(no_args_is_help=True)
console = Console()


@app.command(help="Analyze build context and report optimizations")
def scan(
    dockerfile: Path = typer.Argument(Path("Dockerfile"), help="Path to Dockerfile"),
    context: Path = typer.Argument(Path("."), help="Build context directory"),
    output: Optional[Path] = typer.Option(None, "-o", help="JSON report path"),
    write_ignore: bool = typer.Option(False, "--write-ignore", help="Write .dockerignore"),
    force: bool = typer.Option(False, "--force", help="Overwrite .dockerignore"),
) -> None:
    """Scan Dockerfile for used files, compute savings, suggest .dockerignore."""

    dockerfile = dockerfile.resolve()
    context = context.resolve()

    if not dockerfile.exists():
        typer.echo(f"❌ Dockerfile not found: {dockerfile}", err=True)
        raise typer.Exit(1)

    if not context.exists():
        typer.echo(f"❌ Context dir not found: {context}", err=True)
        raise typer.Exit(1)

    console.print(f"[bold blue]Analyzing[/]: {dockerfile} → {context}")

    # Parse
    patterns = parse_copy_patterns(dockerfile)
    console.print(f"📋 Found {len(patterns)} COPY patterns: {', '.join(patterns[:5])}{'...' if len(patterns)>5 else ''}")

    if not patterns:
        console.print("⚠️  No relevant COPY/ADD found (only --from=?)")

    # Analyze
    all_sizes = get_all_file_sizes(context)
    used_paths = get_used_files(context, patterns)
    used_sizes = {p: all_sizes.get(p, 0) for p in used_paths}

    stats = print_report(context, all_sizes, used_sizes, console)

    # Output JSON
    if output:
        stats["used_files"] = list(used_paths)
        import json
        output.write_text(json.dumps(stats, indent=2))
        console.print(f"💾 JSON report: {output}")

    # Generate .dockerignore
    if write_ignore:
        unused_paths = set(all_sizes) - used_paths
        ignore_content = generate_dockerignore(unused_paths, context)
        ignore_path = context / ".dockerignore"
        if ignore_path.exists() and not force:
            console.print("⚠️  .dockerignore exists. Use --force to overwrite.")
        else:
            ignore_path.write_text(ignore_content)
            console.print(f"✨ Wrote {len(ignore_content.splitlines())} rules to {ignore_path}")


if __name__ == "__main__":
    app()
