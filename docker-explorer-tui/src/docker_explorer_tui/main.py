"""CLI entrypoint for the Docker Explorer TUI app."""

from docker_explorer_tui.app import DockerExplorerApp


def run_app() -> None:
    """Launch the main TUI application."""
    app = DockerExplorerApp()
    app.run()


if __name__ == "__main__":
    run_app()