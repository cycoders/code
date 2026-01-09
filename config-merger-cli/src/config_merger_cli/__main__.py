def main() -> None:
    """Entry point for console script."""
    from .cli import app

    app(prog_name="config-merger-cli")


if __name__ == "__main__":
    main()