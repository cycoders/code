import typer
from pathlib import Path
from rich.table import Table
from rich import print as rprint
from rich.panel import Panel

from . import Detector, Anonymizer, load_config, load_dataframe, save_dataframe
from .types import AnonymizeMode, PIIColumnStats
from .utils import console

app = typer.Typer(help="PII Anonymizer CLI", pretty_exceptions_enable=False)

@app.command()
def detect(
    file_path: Path = typer.Argument(..., help="Input file"),
    format: str = typer.Option("auto", "--format/-f", help="[csv|json|auto]"),
    config: Optional[Path] = typer.Option(None, "--config/-c"),
    min_confidence: float = typer.Option(0.05, "--min-confidence"),
):
    """Scan file for PII statistics."""
    cfg = load_config(config)
    df = load_dataframe(file_path, format)

    detector = Detector(threshold=min_confidence, patterns=cfg.get("patterns", {}))
    stats = detector.detect_column_stats(df)

    if not stats:
        rprint("[green]No PII detected above threshold![/green]")
        raise typer.Exit(0)

    table = Table(title="PII Detection Results")
    table.add_column("Column")
    table.add_column("PII %", justify="right")
    table.add_column("Matches", justify="right")
    table.add_column("Type")

    for stat in stats:
        table.add_row(
            stat.column,
            f"{stat.pii_percentage:.1%}",
            str(stat.match_count),
            stat.dominant_type or "mixed",
        )

    rprint(Panel(table, title=f"[bold cyan]{file_path.name}[/bold cyan] ({len(df)} rows)"))


@app.command()
def preview(
    file_path: Path = typer.Argument(..., help="Input file"),
    rows: int = typer.Option(10, "--rows"),
    format: str = typer.Option("auto", "--format/-f"),
    config: Optional[Path] = typer.Option(None, "--config/-c"),
    mode: str = typer.Option("fake", "--mode"),
):
    """Preview anonymization on first N rows."""
    cfg = load_config(config)
    df = load_dataframe(file_path, format).head(rows)

    detector = Detector(threshold=cfg["threshold"])
    anonymizer = Anonymizer(AnonymizeMode(mode), cfg.get("salt"))

    preview_df = df.copy()
    for col in df.columns:
        mask, ptype = detector.get_pii_mask_and_type(df[col])
        preview_df[col] = anonymizer.anonymize_series(df[col], mask, ptype)

    table = Table.grid(expand=True)
    table.add_column("Original", style="cyan")
    table.add_column("Anonymized", style="green")
    for _, row in df.head(1).iterrows():
        orig = " | ".join(str(v) for v in row)
        anon = " | ".join(str(v) for v in preview_df.loc[row.name])
        table.add_row(orig, anon)

    rprint(Panel(table, title=f"Preview ({rows} rows, mode: {mode})"))


@app.command()
def anonymize(
    file_path: Path = typer.Argument(..., help="Input file"),
    output: Optional[Path] = typer.Option(None, "--output/-o", help="Output file"),
    format: str = typer.Option("auto", "--format/-f"),
    out_format: str = typer.Option("same", "--out-format"),
    dry_run: bool = typer.Option(False, "--dry-run"),
    config: Optional[Path] = typer.Option(None, "--config/-c"),
    mode: str = typer.Option(None, "--mode"),
    seed: Optional[int] = typer.Option(None, "--seed"),
    salt: Optional[str] = typer.Option(None, "--salt"),
):
    """Anonymize PII and save to output."""
    cfg = load_config(config)
    mode = AnonymizeMode(mode or cfg["default_mode"])
    df = load_dataframe(file_path, format)

    detector = Detector(threshold=cfg["threshold"])
    anonymizer = Anonymizer(mode, salt or cfg.get("salt"), seed)

    result_df = df.copy()
    from tqdm import tqdm
    for col in tqdm(list(df.columns), desc="Anonymizing"):
        mask, ptype = detector.get_pii_mask_and_type(df[col])
        if mask.any():
            result_df[col] = anonymizer.anonymize_series(df[col], mask, ptype)

    out_fmt = out_format if out_format != "same" else format
    if output is None:
        output = file_path.parent / f"anon.{'csv' if out_fmt == 'csv' else 'jsonl'}"

    if dry_run:
        rprint("[yellow]Dry-run: No file saved.[/yellow]")
        rprint(result_df.head())
    else:
        save_dataframe(result_df, output, out_fmt)


if __name__ == "__main__":
    app()