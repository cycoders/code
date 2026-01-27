import sys
import typer
from pathlib import Path

from git_bloat_analyzer import analyzer, git_commands, visualizer
from git_bloat_analyzer.types import BlobInfo, PackInfo, RepoStats

app = typer.Typer(add_completion=False)


@app.command(help="Analyze Git repo for bloat.")
def analyze(
    repo: Path = typer.Argument(Path("."), exists=True, file_ok=False),
    top_n: int = typer.Option(20, "--top-n", min=1, max=100),
    min_size_kb: int = typer.Option(1024, "--min-size-kb"),
    json: Path = typer.Option(None, "--json", help="Export JSON report"),
    verbose: bool = typer.Option(False, "--verbose"),
):
    if verbose:
        typer.echo(f"Scanning {repo}...")

    if not git_commands.is_git_repo(repo):
        raise typer.Exit("Not a Git repository.", code=1)

    try:
        stats: RepoStats = analyzer.get_repo_stats(repo)
        blobs: List[BlobInfo] = analyzer.get_large_blobs(repo, top_n, min_size_kb)
        packs: List[PackInfo] = analyzer.get_pack_stats(repo)

        if json:
            visualizer.export_json(stats, blobs, packs, json)
        else:
            visualizer.print_report(stats, blobs, packs)

    except Exception as e:
        typer.echo(f"Error: {e}", err=True)
        raise typer.Exit(code=1) from e


def main():
    if sys.version_info < (3, 11):
        print("Python 3.11+ required.", file=sys.stderr)
        sys.exit(1)
    app(prog_name="git-bloat-analyzer")


if __name__ == "__main__":
    main()