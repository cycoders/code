import typer
from pathlib import Path
from typing_extensions import Annotated

import rich.console

from font_subsetter.extractor import extract_glyphs_from_dir
from font_subsetter.subsetter import subset_fonts

app = typer.Typer(no_args_is_help=True)
console = rich.console.Console()

@app.command()
def main(
    input_dir: Path = typer.Argument(Path("."), help="Project dir to scan"),
    fonts: Annotated[list[Path], typer.Argument()] = typer.Argument([], help="Font files"),
    output_dir: Path = typer.Option(Path("./fonts-subset"), "--output", "-o", help="Output dir"),
    extensions: list[str] = typer.Option(
        [".html", ".htm", ".css", ".js", ".jsx", ".ts", ".tsx", ".svelte", ".vue"],
        "--extensions",
        "-e",
        help="File extensions to scan",
    ),
    dry_run: bool = typer.Option(False, "--dry-run", help="Scan only, no subset"),
):
    """Scan web project and subset fonts by used glyphs."""

    input_dir = input_dir.resolve()
    if not input_dir.exists():
        raise typer.BadParameter(f"Input dir not found: {input_dir}")

    if not fonts:
        # Auto-find common font locations
        search_paths = [
            input_dir / "fonts",
            input_dir / "public" / "fonts",
            input_dir / "static" / "fonts",
        ]
        fonts = []
        font_exts = {*".ttf", *".otf", *".woff", *".woff2", *".eot"}
        for sp in search_paths:
            if sp.exists():
                fonts.extend(sp.rglob("*"))
        fonts = [f for f in fonts if f.suffix.lower() in font_exts]

    if not fonts:
        raise typer.BadParameter("No fonts found. Use --fonts or place in /fonts/")

    console.print(f"[bold blue]Scanning {input_dir}...[/]")
    glyphs = extract_glyphs_from_dir(input_dir, extensions)

    if not glyphs:
        console.print("[yellow]No glyphs found. Check extensions/files.[/]")
        raise typer.Exit(1)

    min_cp, max_cp = min(glyphs), max(glyphs)
    console.print(f"[green]Found {len(glyphs)} glyphs (U+{min_cp:04X}..U+{max_cp:04X})[/]")

    if dry_run:
        console.print("[yellow]Dry-run: glyphs extracted.[/]")
        raise typer.Exit(0)

    output_dir.mkdir(exist_ok=True)
    stats = subset_fonts(fonts, glyphs, output_dir)

    from rich.table import Table
    table = Table(title="Font Subsetting Results")
    table.add_column("Font")
    table.add_column("Original", justify="right")
    table.add_column("Subset", justify="right")
    table.add_column("Savings")

    total_orig = total_sub = 0
    for name, orig, sub, pct, glyphs_used, glyphs_total in stats:
        table.add_row(
            name,
            f"{orig/1024:.1f}KB",
            f"{sub/1024:.1f}KB",
            f"{pct:.0f}% ↓",
        )
        total_orig += orig
        total_sub += sub

    avg_pct = ((total_orig - total_sub) / total_orig * 100) if total_orig else 0
    table.add_row("[bold]TOTAL[/]", f"{total_orig/1024:.1f}KB", f"{total_sub/1024:.1f}KB", f"{avg_pct:.0f}% ↓")

    console.print(table)

    console.print(f"[bold green]Subsets saved in {output_dir}[/]")

if __name__ == "__main__":
    app()