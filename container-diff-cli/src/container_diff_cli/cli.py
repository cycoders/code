import typer
from typing_extensions import Annotated

from .differ import compute_diff
from .renderer import render_diff

app = typer.Typer(help="Container image diffs.")

FormatChoice = Annotated[str, typer.Option("table", "--format", "-f", help="Output format")]


@app.command()
def diff(
    image1: str = typer.Argument(..., help="First image"),
    image2: str = typer.Argument(..., help="Second image"),
    fmt: FormatChoice = "table",
):
    """
    Diff two images.

    Auto-pulls if needed.
    """
    diff_result = compute_diff(image1, image2)
    render_diff(diff_result, fmt)


if __name__ == "__main__":
    app()