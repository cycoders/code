# Additional screens if needed

from textual.screen import Screen


class ConfigScreen(Screen):
    """Config editor screen."""

    def compose(self):
        yield Input(placeholder="Base URL", id="base_url")
        yield Input(placeholder="API Key", id="api_key", password=True)
        yield Input(placeholder="Model", id="model")
        yield Button("Save", id="save")

    def on_button_pressed(self, event):
        if event.button.id == "save":
            # Save and pop
            pass
