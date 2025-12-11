from reqbench.cli import app

if __name__ == "__main__":
    import sys
    from typer.main import get_command_from_cli_app
    cli_app = get_command_from_cli_app(app, standalone_mode=False)
    cli_app(sys.argv[1:] if len(sys.argv) > 1 else ["--help"])