import typer
from typing import Optional
import json

from rich.console import Console
from rich.progress import Progress

from .parser import parse_har
from .generators import get_generator_class


app = typer.Typer(add_completion=False)
console = Console()


@app.command(help="Generate load test script from HAR file")
def gen(
    har_file: str = typer.Argument(..., help="Path to HAR file"),
    fmt: str = typer.Option("k6", "--format", "-f", help="k6, locust, or artillery"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path (default: stdout)"),
    vus: int = typer.Option(10, "--vus", "-V", help="Virtual users/concurrency"),
    duration: str = typer.Option("30s", "--duration", "-d", help="Test duration (e.g., 30s, 5m)"),
    think_time: float = typer.Option(1.0, "--think-time", "-t", min=0.0, help="Sleep between requests"),
) -> None:
    """Generate load test script from HAR."""
    try:
        with Progress(console=console) as progress:
            parse_task = progress.add_task("[cyan]Parsing HAR...", total=None)
            requests = parse_har(har_file)
            progress.remove_task(parse_task)

            gen_task = progress.add_task("[cyan]Generating code...", total=None)
            generator_cls = get_generator_class(fmt)
            generator = generator_cls(requests, vus=vus, duration=duration, think_time=think_time)
            code = generator.generate()
            progress.remove_task(gen_task)

        if output:
            with open(output, "w", encoding="utf-8") as f:
                f.write(code)
            console.print(f"[green]✅ Script written to {output}")
        else:
            console.print("[bold cyan]# Generated script:\n")
            console.print(code)

        console.print(f"\n[green]✓ Generated {len(requests)} requests ({fmt.upper()}). Run with your tool!")

    except FileNotFoundError:
        typer.echo(f"[red]Error:[/red] HAR file '{har_file}' not found.", err=True)
        raise typer.Exit(code=1)
    except KeyError as e:
        typer.echo(f"[red]Error:[/red] Invalid HAR structure: missing {e}", err=True)
        raise typer.Exit(code=1)
    except ValueError as e:
        typer.echo(f"[red]Error:[/red] {e}", err=True)
        raise typer.Exit(code=1)
    except Exception as e:
        typer.echo(f"[red]Unexpected error:[/red] {str(e)}", err=True)
        raise typer.Exit(code=1)


def main() -> None:
    """Entry point for the CLI."""
    if __name__ == "__main__":
        app()
    else:
        app(prog_name="har-to-loadtest")
