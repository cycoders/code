import json
import sys
import typer
from datetime import datetime, timedelta
from typing import Optional
from zoneinfo import ZoneInfo

from cron_simulator.parser import parse_jobs, parse_datetime
from cron_simulator.simulator import simulate_jobs, detect_overlaps
from cron_simulator.visualizer import print_summary, print_exec_table, print_gantt
from cron_simulator.models import Job, Execution


app = typer.Typer(help="Cron Simulator: Simulate, predict, visualize cron schedules.")


@app.command()
def sim(
    config: Optional[typer.Path] = typer.Option(None, "--config", help="YAML jobs file"),
    cron: Optional[str] = typer.Option(None, "--cron", help="Single cron expression"),
    start: str = typer.Option("2024-01-01T00:00:00", "--start", help="Start ISO datetime"),
    end: str = typer.Option("2024-01-02T00:00:00", "--end", help="End ISO datetime"),
    tz: str = typer.Option("UTC", "--tz", help="Timezone"),
    output: str = typer.Option("summary", "--output", help="Output mode"),
):
    """Simulate cron jobs over a time range."""
    if config is None and cron is None:
        typer.echo("Error: Provide --config or --cron", err=True)
        raise typer.Exit(1)

    try:
        start_dt = parse_datetime(start, tz)
        end_dt = parse_datetime(end, tz)
        if start_dt >= end_dt:
            raise ValueError("start must precede end")
    except ValueError as e:
        typer.echo(f"Invalid datetime: {e}", err=True)
        raise typer.Exit(1)

    if config:
        jobs = parse_jobs(config)
    else:
        jobs = [Job(name="job", cron=cron, duration=60)]

    executions = simulate_jobs(jobs, start_dt, end_dt)
    overlaps = detect_overlaps(executions)

    print_summary(executions, overlaps)

    match output:
        case "gantt":
            print_gantt(executions, start_dt, end_dt)
        case "table":
            print_exec_table(executions)
        case "json":
            print(json.dumps([asdict(e) for e in executions], default=str, indent=2))
        case _:
            pass


@app.command()
def predict(
    cron: str,
    count: int = typer.Option(5, "--count"),
    tz: str = typer.Option("UTC", "--tz"),
    from_: str = typer.Option("now", "--from"),
):
    """Predict next N runs."""
    from zoneinfo import ZoneInfo
    from datetime import datetime
    from croniter import croniter

    now = datetime.now(ZoneInfo(tz)) if from_ == "now" else parse_datetime(from_, tz)

    try:
        it = croniter(cron, now)
        for i in range(count):
            next_run = it.get_next(datetime)
            typer.echo(next_run.strftime("%Y-%m-%d %H:%M:%S %Z"))
    except Exception as e:
        typer.echo(f"Invalid cron '{cron}': {e}", err=True)
        raise typer.Exit(1)


@app.command()
def validate(cron: str, tz: str = "UTC"):
    """Validate a cron expression."""
    from croniter import croniter
    from datetime import datetime
    from zoneinfo import ZoneInfo

    now = datetime.now(ZoneInfo(tz))
    try:
        it = croniter(cron, now)
        next_run = it.get_next(datetime)
        typer.echo(f"Valid cron '{cron}'. Next run: {next_run}")
    except Exception as e:
        typer.echo(f"Invalid cron '{cron}': {e}", err=True)
        raise typer.Exit(1)


if __name__ == "__main__":
    app()