from textual import on, work, events
from textual.binding import Binding
from textual.message import Message
from textual.reactive import reactive
from textual.widget import Widget
from textual.widgets import Button, Label, Static, ListView, ListItem
from textual.app import ComposeResult

import rich.markup

from .tokenizer import Tokenizer


class TokenCounter(Static):
    """Live token counter."""

    DEFAULT_CSS = """
    TokenCounter {
        dock: bottom;
        height: 1;
        background: $primary;
        color: $text;
    }
    """

    tokens = reactive(0)

    def watch_tokens(self, tokens: int) -> None:
        self.update(f"[Tokens: {tokens}] ")


class PromptEditor(Static):
    """Custom prompt editor with live tokens."""

    DEFAULT_CSS = """
    PromptEditor {
        height: 1fr;
        max-height: 10;
    }
    """

    text = reactive("")

    BINDINGS = [Binding("enter", "submit", "Submit", show=False)]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.tokenizer = Tokenizer()

    def compose(self) -> ComposeResult:
        yield Label("System Prompt:")
        yield Static(id="system-prompt")
        yield Label("User Prompt:")
        yield Static(id="user-prompt", classes="prompt-input")

    def watch_text(self, text: str) -> None:
        # Simulate live update
        pass

    @on(events.Key)
    def on_key(self, event: events.Key) -> None:
        if event.key.is_printable:
            self.text += event.key.character


class ResponseViewer(Static):
    """Response display with scores."""

    DEFAULT_CSS = """
    ResponseViewer {
        height: 1fr;
    }
    """

    def compose(self) -> ComposeResult:
        yield Static(id="response-text")
        yield Static(id="scores")


class HistoryList(ListView):
    """Session history."""

    def compose(self) -> ComposeResult:
        yield ListItem(Label("No history yet"), id="no-history")

    def on_list_view_selected(self, event: ListView.Selected) -> None:
        # Load prompt
        pass
