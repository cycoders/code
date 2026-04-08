import typer
import json
from pathlib import Path
from typing import List

from rich.console import Console
from rich_click import rich_click

from .benchmark import measure
from .formats import get_serializer, FORMAT_NAMES
from .generator import generate_sample_data
from .reporter import print_results


rich_click.typer_rich_status()
app = typer.Typer(help="SerDes Bench", rich_markup_mode="rich")
console = Console()


@app.command()
def bench(
    input_file: Path = typer.Argument(
        None, help="Input JSON file with sample data (mutually exclusive with --generate)"
    ),
    generate: str = typer.Option(
        None, "--generate/-g", help="Generate data: 'simple', 'nested', 'array-heavy'"
    ),
    gen_size: int = typer.Option(1000, "--size", help="Approx #items for generated data"),
    formats: List[str] = typer.Option(
        ["all"], "--format/-f", help="Formats: all or [json,orjson,ujson,msgpack,cbor]"
    ),
    iters: int = typer.Option(10000, "--iters/-i", min=1, help="Benchmark iterations"),
    warmup: int = typer.Option(10, "--warmup", min=0, help="Warmup iterations"),
    export: Path = typer.Option(None, "--export/-e", help="Export results as JSON"),
):
    """Benchmark ser/de formats on data."""

    if bool(input_file) == bool(generate):
        typer.echo("Exactly one of --input or --generate required.")
        raise typer.Exit(1)

    if input_file:
        if not input_file.is_file():
            raise typer.BadParameter(f"File not found: {input_file}")
        try:
            with input_file.open("r") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise typer.BadParameter(f"Invalid JSON: {e}")
    else:
        try:
            data = generate_sample_data(generate, gen_size)
        except ValueError as e:
            raise typer.BadParameter(str(e))

    selected_formats = formats if formats != ["all"] else FORMAT_NAMES
    selected_formats = [f for f in selected_formats if f in FORMAT_NAMES]
    if not selected_formats:
        raise typer.BadParameter(f"Invalid formats. Available: {', '.join(FORMAT_NAMES)}")

    serializers = {name: get_serializer(name) for name in selected_formats}

    results = []
    with typer.progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        console=console,
    ) as p:
        task = p.add_task("Benchmarking...", total=len(serializers))
        for name in selected_formats:
            ser = serializers[name]
            result = measure(ser, data, iters, warmup)
            results.append(result)
            p.advance(task)

    print_results(console, results)

    if export:
        import json
        export.write_text(json.dumps([r.__dict__ for r in results], indent=2))
        console.print(f"[green]Exported to {export}")


if __name__ == "__main__":
    app()
