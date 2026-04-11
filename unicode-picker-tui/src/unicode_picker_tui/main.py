"""CLI entrypoint for Unicode Picker TUI."""

from .app import CharPickerApp


def run() -> None:
    """Run the application."""
    app = CharPickerApp("Unicode Picker TUI", id="charpicker")
    app.run()