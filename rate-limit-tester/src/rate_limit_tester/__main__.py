import sys

from typer import run

from .cli import app


def main():
    """Entry point for the CLI."""
    if len(sys.argv) == 1:
        sys.argv.append("--help")  # Show help if no args

    run(app)


if __name__ == "__main__":
    main()
