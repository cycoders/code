import typer
from pathlib import Path
from typing import Annotated, Optional

import rich.console
from rich.table import Table
from rich import print as rprint

from .differ import compute_similarity, SimilarityResult
from .batch import batch_compare

app = typer.Typer(pretty_exceptions_enable=False)
console = rich.console.Console()

ResizeMode = typer.Literal["none", "fit", "crop"]
DiffMode = typer.Literal["side-by-side", "heatmap", "overlay"]

@app.command(help="Compare two images")
def diff(
    img1: Path = typer.Argument(..., exists=True, readable=True),
    img2: Path = typer.Argument(..., exists=True, readable=True),
    output: Optional[Path] = typer.Option(None, "--output", "-o", help="Output dir/file prefix"),
    threshold: float = typer.Option(0.02, "--fail-above/-t", help="Fail if max_diff > this (SSIM delta)"),
    resize: ResizeMode = typer.Option("fit", "--resize", help="Handle size mismatch"),
    mode: DiffMode = typer.Option("heatmap", "--mode", "-m", help="Visualization style"),
    json: bool = typer.Option(False, "--json/-j", help="JSON output"),
    config: Optional[Path] = typer.Option(None, "--config", help="YAML config"),
):
    """Compute perceptual diff between two images."""
    result: SimilarityResult = compute_similarity(str(img1), str(img2), resize=resize)

    max_diff = 1 - result.ssim  # Convert to 'diff' scale 0-1
    if max_diff > threshold:
        rprint(f"[red bold]FAIL[/]: SSIM {result.ssim:.4f} (diff {max_diff:.4f}) > {threshold}")
        raise typer.Exit(code=1)

    rprint("[green bold]PASS ✅[/]")
    _print_metrics(result)

    if output:
        output.mkdir(exist_ok=True, parents=True)
        result.save_visualizations(output / f"{img1.stem}_vs_{img2.stem}", mode)
        rprint(f"[blue]Saved[/] to {output}")

    if json:
        typer.echo(result.to_json())

@app.command(help="Batch compare image folders")
def batch(
    before: Path = typer.Argument(..., exists=True),
    after: Path = typer.Argument(..., exists=True),
    output: Path = typer.Option("batch-report", "--output/-o"),
    threshold: float = typer.Option(0.02, "--fail-above/-t"),
    resize: ResizeMode = "fit",
    mode: DiffMode = "heatmap",
    json: bool = False,
    csv: bool = False,
):
    """Pair images by name across folders (before/a.png ↔ after/a.png)."""
    results = batch_compare(before, after, threshold, resize, mode)

    total = len(results)
    failures = sum(1 for r in results if r.max_diff > threshold)

    table = Table(title="Batch Report")
    table.add_column("File")
    table.add_column("SSIM")
    table.add_column("Status")
    for r in results:
        status = "[red]FAIL[/]" if r.max_diff > threshold else "[green]PASS[/]"
        table.add_row(r.basename, f"{r.ssim:.4f}", status)

    console.print(table)
    rprint(f"[bold]{failures}/{total} failures[/]")

    if failures > 0:
        raise typer.Exit(1)

    # Save outputs
    output.mkdir(exist_ok=True)
    for r in results:
        out_path = output / r.basename
        r.save_visualizations(out_path, mode)

    if json:
        typer.echo("[{" + ",".join(r.to_json() for r in results) + "]")

    if csv:
        # Simplified CSV
        typer.echo("basename,ssim,psnr,mse")
        for r in results:
            typer.echo(f"{r.basename},{r.ssim},{r.psnr},{r.mse}")

@app.command()
def config():
    typer.echo("YAML config example:")
    typer.echo("threshold: 0.015")
    typer.echo("mode: heatmap")
    typer.echo("resize: fit")

if __name__ == "__main__":
    app()

def _print_metrics(result: SimilarityResult):
    table = Table.grid(expand=True)
    table.add_row("Metric", "Value")
    table.add_row("SSIM", f"{result.ssim:.4f}")
    table.add_row("PSNR", f"{result.psnr:.2f}dB")
    table.add_row("MSE", f"{result.mse:.4f}")
    console.print(table)
