import typer
from pathlib import Path
import yaml
from typing import Optional

from rich.console import Console

from .config import BackfillConfig
from .planner import BackfillPlanner
from .renderer import render_plan


app = typer.Typer(no_args_is_help=True, pretty_exceptions_enable=False)
console = Console()


@app.command(help="Generate a detailed backfill plan")
def plan(
    config_file: Path = typer.Argument(..., help="YAML config file path"),
    write_throughput_avg: Optional[float] = typer.Option(None, "--write-throughput-avg", min=0),
    strategy: Optional[str] = typer.Option(None, "--strategy"),
):
    """Plan a safe database backfill migration."""
    try:
        if not config_file.exists():
            raise typer.BadParameter(f"Config file not found: {config_file}")

        with open(config_file, "r") as f:
            data = yaml.safe_load(f)

        config_dict = dict(data)
        if write_throughput_avg:
            config_dict["write_throughput_avg"] = write_throughput_avg
        if strategy:
            config_dict["strategy"] = strategy

        config = BackfillConfig.model_validate(config_dict)

        planner = BackfillPlanner(config)
        plan = planner.generate_plan()

        render_plan(plan, console)

    except Exception as e:
        console.print(f"[red bold]Error:[/red bold] {str(e)}")
        raise typer.Exit(code=1) from e


if __name__ == "__main__":
    app()