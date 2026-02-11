import sys

from rich.console import Console

from .cli import app


def main():
    try:
        app()
    except KeyboardInterrupt:
        Console().print("[yellow]Interrupted.[/]")
        sys.exit(1)
    except Exception as e:
        Console(stderr=True).print(f"[red]Error: {e}[/]")
        sys.exit(1)


if __name__ == "__main__":
    main()