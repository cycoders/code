import typer
from rich.console import Console
from rich.progress import track
from pathlib import Path
import multiprocessing as mp
from .query import find_matches
from .patterns import Pattern

app = typer.Typer()
console = Console()

@app.command()
def main(pattern: str, paths: list[Path]):
    p = Pattern(ast.Call, {"func.attr": "execute"})  # example
    with ProcessPoolExecutor(max_workers=mp.cpu_count()) as ex:
        results = []
        for pth in track(paths, description="Scanning"):
            results.extend(ex.submit(find_matches, pth, p).result())
    for path, lineno in results:
        console.print(f"{path}:{lineno}")