from textual.app import App

from .app import PromptPlaygroundApp


def main() -> None:
    """Entry point for the CLI."""
    app = PromptPlaygroundApp()
    app.run()


if __name__ == "__main__":
    main()
