import sys

from .cli import app


if __name__ == "__main__":
    app(prog_name="logq")
    sys.exit(0)