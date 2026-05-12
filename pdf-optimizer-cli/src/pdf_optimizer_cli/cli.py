import typer
import pathlib
from typing import Optional

from rich import print as rprint
from rich.table import Table
from rich.live import Live
from rich.progress import Progress, SpinnerColumn, TextColumn

from pdf_optimizer_cli.optimizer import optimize_pdf, get_stats, batch_optimize

app = typer.Typer(help="Optimizes PDF files for size without quality loss.")

@app.command(help="Optimize a single PDF file.")
def optimize(
    input_path: pathlib.Path = typer.Argument(..., exists=True, help="Input PDF path"),
    output_path: Optional[pathlib.Path] = typer.Option(None, "-o", "--output", help="Output path (default: input-opt.pdf)"),
    quality: int = typer.Option(85, "-q", "--quality", min=10, max=100, help="JPEG quality (10-100)"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview savings without saving"),
):
    """Optimize a single PDF."""
    if output_path is None:
        stem = input_path.stem
        output_path = input_path.with_name(f"{stem}-opt.pdf")

    if dry_run:
        size_before = input_path.stat().st_size
        stats = get_stats(input_path, quality)
        estimated_size = size_before - stats["bytes_saved"]
        rprint_stats(input_path, size_before, estimated_size, stats["bytes_saved"], stats)
        return

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        task = progress.add_task("Optimizing...", total=None)
        optimize_pdf(str(input_path), str(output_path), quality)
        progress.remove_task(task)

    size_after = output_path.stat().st_size
    size_before = input_path.stat().st_size
    savings = size_before - size_after
    stats = get_stats(input_path, quality)  # approx
    rprint_stats(input_path, size_before, size_after, savings, stats)


@app.command(help="Batch optimize all PDFs in a directory.")
def batch(
    input_dir: pathlib.Path = typer.Argument(..., exists=True, help="Input directory"),
    output_dir: Optional[pathlib.Path] = typer.Option("optimized", "--output-dir", help="Output directory"),
    quality: int = typer.Option(85, "--quality", min=10, max=100),
    dry_run: bool = typer.Option(False, "--dry-run"),
    recursive: bool = typer.Option(True, "--recursive", help="Scan subdirs"),
):
    """Batch optimize PDFs."""
    output_dir = pathlib.Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    pdfs = list(input_dir.rglob("*.pdf") if recursive else input_dir.glob("*.pdf"))
    if not pdfs:
        rprint("[red]No PDF files found.[/red]")
        raise typer.Exit(1)

    table = Table(title="Optimization Results")
    table.add_column("File")
    table.add_column("Before")
    table.add_column("After")
    table.add_column("Savings")

    total_before, total_after, total_saved = 0, 0, 0

    with Live(table, refresh_per_second=10):
        for pdf_path in tqdm(pdfs, desc="Processing"):
            rel_path = pdf_path.relative_to(input_dir)
            out_path = output_dir / rel_path.with_name(f"{rel_path.stem}-opt.pdf")
            out_path.parent.mkdir(parents=True, exist_ok=True)

            size_before = pdf_path.stat().st_size
            total_before += size_before

            if dry_run:
                stats = get_stats(pdf_path, quality)
                est_size = size_before - stats["bytes_saved"]
                savings_pct = (stats["bytes_saved"] / size_before) * 100
                table.add_row(str(rel_path), f"{size_before/1024/1024:.1f} MiB", f"~{est_size/1024/1024:.1f} MiB", f"{savings_pct:.0f}%")
                total_after += est_size
                total_saved += stats["bytes_saved"]
            else:
                optimize_pdf(str(pdf_path), str(out_path), quality)
                size_after = out_path.stat().st_size
                savings = size_before - size_after
                savings_pct = (savings / size_before) * 100
                table.add_row(str(rel_path), f"{size_before/1024/1024:.1f} MiB", f"{size_after/1024/1024:.1f} MiB", f"{savings_pct:.0f}%")
                total_after += size_after
                total_saved += savings

    rprint(f"\n[bold green]Total: {total_before/1024/1024:.1f} → {total_after/1024/1024:.1f} MiB ({(total_saved/total_before)*100:.0f}% saved)[/bold green]")


def rprint_stats(input_path, size_before, size_after, savings, stats):
    table = Table(title="Optimization Summary")
    table.add_column("Metric")
    table.add_column("Value")
    table.add_row("File", str(input_path.name))
    table.add_row("Before", f"{size_before / 1024**2:.1f} MiB")
    table.add_row("After", f"{size_after / 1024**2:.1f} MiB")
    table.add_row("Savings", f"{(savings / size_before * 100):.0f}%")
    table.add_row("Images optimized", f"{stats['images_optimized']}/{stats['images_total']}")
    table.add_row("Bytes saved (images)", f"{stats['bytes_saved'] / 1024 / 1024:.1f} MiB")
    rprint(table)

if __name__ == "__main__":
    app()