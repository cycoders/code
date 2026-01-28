import typer
from pathlib import Path
from typing import List

from rich.console import Console
from rich.table import Table
from rich.live import Live
from rich.progress import track
import rich.progress
from rich.panel import Panel
from rich.prompt import Confirm

from .optimizer import optimize_image
from .preview import image_to_ascii, side_by_side_ascii
from .utils import get_image_files, ensure_dir

app = typer.Typer(no_args_is_help=True)
console = Console()

@app.command()
def optimize(
    path: Path = typer.Argument(..., help="Path to image file or directory"),
    output: Path = typer.Option(Path("optimized"), "--output", "-o", help="Output directory"),
    fmt: str = typer.Option("auto", "--format", "-f", help="Output format (jpg, png, webp, avif, auto)"),
    quality: int = typer.Option(85, "--quality", "-q", min=10, max=100, help="Quality (10-100)"),
    preview: bool = typer.Option(False, "--preview", help="Interactive ASCII preview (single file)"),
    dry_run: bool = typer.Option(False, "--dry-run", "-n", help="Show stats without saving"),
    recursive: bool = typer.Option(False, "--recursive", "-r", help="Recurse directories"),
) -> None:
    """Optimize images for web with previews and stats."""

    files: List[Path] = get_image_files(str(path), recursive)
    if not files:
        typer.echo("❌ No supported images found (.jpg, .png, .webp, .avif, .tiff).", err=True)
        raise typer.Exit(code=1)

    ensure_dir(output)
    results = []

    # Single-file preview mode
    if len(files) == 1 and preview:
        file_path = files[0]
        console.print(f"🔍 Processing [bold]{file_path.name}[/bold]")
        result = optimize_image(str(file_path), fmt, quality)

        from PIL import Image
from io import BytesIO
        orig_img = Image.open(file_path)
        opt_img = Image.open(BytesIO(result["optimized_image"]))

        orig_ascii = image_to_ascii(orig_img, width=60, height=25)
        opt_ascii = image_to_ascii(opt_img, width=60, height=25)
        diff_ascii = side_by_side_ascii(orig_ascii, opt_ascii, width=60)

        console.print(Panel(diff_ascii, title=f"Preview: {fmt.upper()} q{quality}", border_style="blue"))

        if not Confirm.ask("💾 Proceed with save?"):
            console.print("👋 Aborted.")
            return

        results.append(result)
    else:
        # Batch mode
        console.print(f"🚀 Optimizing [bold]{len(files)}[/bold] images...")
        for file_path in track(files, description="Optimizing..."):
            try:
                result = optimize_image(str(file_path), fmt, quality)
                results.append(result)
                if not dry_run:
                    out_path = output / file_path.with_suffix(f".result['format']").name
                    with open(out_path, "wb") as f:
                        f.write(result["optimized_image"])
            except Exception as e:
                console.print(f"[red]✗[/red] {file_path.name}: {str(e)[:60]}...")
                continue

    # Results table
    if not results:
        return

    table = Table(title="Optimization Results")
    table.add_column("File", style="cyan")
    table.add_column("Original", justify="right")
    table.add_column("Optimized", justify="right")
    table.add_column("Savings", justify="right")
    table.add_column("Format")

    total_orig = sum(r["original_size"] for r in results)
    total_opt = sum(r["output_size"] for r in results)
    total_savings = ((total_orig - total_opt) / total_orig * 100) if total_orig else 0

    for r in results:
        savings = r["savings_percent"]
        table.add_row(
            Path(r["input"]).name,
            f"{r['original_size']/1024:.1f} KiB",
            f"{r['output_size']/1024:.1f} KiB",
            f"{savings:.1f}%" if savings > 0 else "0%",
            r["format"].upper(),
        )

    console.print(table)

    # Summary panel
    sum_table = Table.grid(expand=True)
    sum_table.add_row("Total Original", f"{total_orig/1024/1024:.2f} MiB")
    sum_table.add_row("Total Optimized", f"{total_opt/1024/1024:.2f} MiB")
    sum_table.add_row(
        "Total Savings",
        f"[green]{total_savings:.1f}%[/green]" if total_savings > 0 else "[red]0%[/red]",
    )
    style = "green" if total_savings > 20 else "yellow" if total_savings > 0 else "red"
    console.print(Panel(sum_table, title="📈 Summary", border_style=style))

    if dry_run:
        console.print("[yellow]Dry-run: no files saved.[/yellow]")
