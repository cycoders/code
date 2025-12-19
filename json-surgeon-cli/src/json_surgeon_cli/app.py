import json
from typing import List, Union, Any
from pathlib import Path
from dataclasses import dataclass
from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static, Tree, Input, Button, Label, Modal
from textual.containers import Horizontal
from textual.message import Message
from textual.binding import Binding
from pyperclip import copy

from .utils import load_json, update_json_at_path, truncate
from .tree_view import JsonTree
from .query_engine import apply_jmespath
from .schema_validator import validate_json


@dataclass
class EditorSubmitted(Message):
    path: List[Union[str, int]]
    value: Any


@dataclass
class ValidationSubmitted(Message):
    errors: List[str]


class EditorModal(Modal):
    """Modal for editing JSON value."""

    def __init__(self, path: List[Union[str, int]], current: Any):
        self.path = path
        self.current = current
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label("Edit Value (JSON):")
        inp = Input(json.dumps(self.current), id="edit-input", placeholder="new value")
        yield inp
        yield Horizontal(Button("Update", id="update", variant="primary"), Button("Cancel", id="cancel"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss()
            return
        inp = self.query_one("#edit-input")
        try:
            new_value = json.loads(inp.value)
            self.post_message(EditorSubmitted(self.path, new_value))
            self.dismiss()
        except json.JSONDecodeError:
            self.query_one("#edit-input").styles.color = "red"


class ValidationModal(Modal):
    """Modal for schema validation."""

    def __init__(self, data: Any):
        self.data = data
        super().__init__()

    def compose(self) -> ComposeResult:
        yield Label("Schema file path:")
        yield Input(id="schema-path", placeholder="schema.json")
        yield Horizontal(Button("Validate", id="validate", variant="primary"), Button("Cancel"))

    def on_button_pressed(self, event: Button.Pressed) -> None:
        if event.button.id == "cancel":
            self.dismiss()
            return
        path = self.query_one("#schema-path", Input).value
        try:
            with open(Path(path)) as f:
                schema = json.load(f)
            is_valid, errors = validate_json(self.data, schema)
            self.post_message(ValidationSubmitted(errors))
            self.dismiss()
        except Exception as e:
            self.notify(f"Error loading schema: {e}", severity="error")


class JsonSurgeonApp(App[None]):
    """Main TUI app."""

    CSS = """
    Static#preview {
        background: $panel;
        color: $text;
        white-space: pre-wrap;
        padding: 1;
        height: 1fr;
    }
    JsonTree {
        height: 1fr;
        width: 45%;
    }
    Input#query-input {
        dock: bottom;
        height: 3;
        width: 1fr;
    }
    """

    BINDINGS = [
        Binding("q", "query", "Query"),
        Binding("e", "edit", "Edit"),
        Binding("v", "validate", "Validate"),
        Binding("f", "format", "Format"),
        Binding("s", "save", "Save"),
        Binding("c", "copy", "Copy"),
        Binding("?", "help", "Help"),
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, json_file: str | None):
        super().__init__()
        try:
            self.json_data: Any = load_json(json_file)
        except Exception as e:
            self.exit(str(e))
        self.tree: JsonTree | None = None
        self.preview: Static | None = None
        self.query_input: Input | None = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True, markdown_title="🔬 JSON Surgeon")
        yield Horizontal(
            self.tree := JsonTree(id="tree"),
            self.preview := Static(id="preview"),
        )
        yield self.query_input := Input(
            "Enter JMESPath query (q)...",
            placeholder="users[0].name",
            id="query-input",
        )
        yield Footer()

    def on_mount(self) -> None:
        self.build_tree()
        self.update_preview()

    def build_tree(self) -> None:
        self.tree.load_tree(self.json_data)

    def update_preview(self, data: Any | None = None) -> None:
        data = data or self.json_data
        self.preview.update(json.dumps(data, indent=2))

    def on_input_entered(self, event: Input.Entered) -> None:
        if event.input.id != "query-input":
            return
        query = event.input.value.strip()
        try:
            result = apply_jmespath(self.json_data, query)
            self.update_preview(result)
        except Exception as e:
            self.notify(f"Query error: {truncate(str(e))}", severity="error")
        event.input.value = ""

    def on_editor_submitted(self, event: EditorSubmitted) -> None:
        update_json_at_path(self.json_data, event.path, event.value)
        self.build_tree()
        self.update_preview()

    def on_validation_submitted(self, event: ValidationSubmitted) -> None:
        if not event.errors:
            self.notify("✅ Schema valid!", severity="success")
        else:
            self.notify(f"❌ Errors:\n{"\n".join(event.errors[:3])}...", severity="error")

    def action_query(self) -> None:
        self.set_focus(self.query_input)

    def action_edit(self) -> None:
        node_data = self.tree.get_cursor_data()
        if not node_data or not node_data["is_leaf"]:
            self.notify("Select a leaf node to edit", severity="warning")
            return
        self.push_screen(EditorModal(node_data["path"], node_data["value"]))

    def action_validate(self) -> None:
        self.push_screen(ValidationModal(self.json_data))

    def action_format(self) -> None:
        self.update_preview()

    def action_save(self) -> None:
        self.notify("Save via `s` modal (future: direct write)", "info")  # Simplified

    def action_copy(self) -> None:
        copy(json.dumps(self.json_data, indent=2))
        self.notify("📋 Copied to clipboard!", "success")

    def action_help(self) -> None:
        help_text = """
q: Query | e: Edit | v: Validate | f: Format | c: Copy | ?: Help | Ctrl+q: Quit
        """
        self.notify(help_text, title="Keybindings")
