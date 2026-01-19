import sys

from typer import Exit

import sql_erd_cli.cli as cli


def main():
    try:
        cli.app(prog_name="sql-erd-cli")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        raise Exit(code=1)


if __name__ == "__main__":
    main()