import sys
import typer
from pathlib import Path
from typing import Dict, List

from .benchmark import benchmark_compressor
from .compressors import get_compressor
from .output import print_results

app = typer.Typer(
    name="compression-benchmarker",
    add_completion=False,
    context_settings={"help_option_names": ["-h", "--help"]},
)

DEFAULT_LEVELS: Dict[str, List[int]] = {
    "gzip": [1, 6, 9],
    "bz2": [1, 5, 9],
    "lzma": [1, 6, 9],
    "brotli": [0, 4, 8, 11],
    "zstd": [1, 3, 10, 22],
    "lz4": [0, 4, 9, 12],
}

@app.command("bench", help="Benchmark compression algorithms on file or stdin")
def bench(
    input_path: str = typer.Argument("-", help="File path or '-' for stdin"),
    algorithms: str = typer.Option("all", "--algo", help="Algos ('all' or comma-sep): gzip,bz2,lzma,brotli,zstd,lz4"),
    levels: str = typer.Option("auto", "--levels", help="Levels ('auto' or comma-sep like '1,6,9')"),
    runs: int = typer.Option(3, "--runs", min=1, max=10, help="Benchmark runs per config"),
    output_fmt: str = typer.Option("table", "--output", "-o", help="Output: table,json,csv"),
    console: typer.Console = typer.console,
) -> None:
    """Benchmark compressors on your data."""

    # Parse algos
    algo_list = [a.strip().lower() for a in algorithms.split(",")]
    if "all" in algo_list:
        algo_list = list(DEFAULT_LEVELS.keys())

    # Parse levels
    level_map: Dict[str, List[int]] = {}
    for algo in algo_list:
        if levels == "auto":
            level_map[algo] = DEFAULT_LEVELS.get(algo, [1])
        else:
            lvls = [int(l.strip()) for l in levels.split(",")]
            level_map[algo] = lvls

    # Read data
    if input_path == "-":
        data = sys.stdin.buffer.read()
        source = "stdin"
    else:
        p = Path(input_path)
        if not p.is_file():
            raise typer.BadParameter(f"'{input_path}' is not a file")
        data = p.read_bytes()
        source = p.name

    orig_size = len(data)
    if orig_size == 0:
        raise typer.Exit(code=1, message="No data to benchmark")

    if orig_size > 2 * 1024**3:
        console.print("[bold yellow]⚠️  Large file (>2GB): Benchmarks accurate, but slow.[/]", emoji="warn")

    console.print(f"[info]Benchmarking {orig_size / 1024**2:.1f} MiB from {source}[/]")

    # Run benchmarks
    results = []
    with console.status("[bold green]Compressing..."):
        for algo, lvls in level_map.items():
            for lvl in lvls:
                try:
                    comp = get_compressor(algo, lvl)
                    res = benchmark_compressor(comp, data, runs)
                    res["algo"] = algo
                    res["level"] = lvl
                    results.append(res)
                except Exception as e:
                    console.print(f"[red]Error on {algo}-{lvl}: {e}[/]", emoji="cross")
                    continue

    print_results(results, orig_size, output_fmt, console)

if __name__ == "__main__":
    app()