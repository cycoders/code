import asyncio
import difflib
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any

from textual.app import App, ComposeResult, on
from textual.containers import Container, Horizontal, VerticalScroll
from textual.message import Message
from textual.screen import Screen
from textual import events, work
from textual.widgets import Footer, Header, Button, Input, Select, Label, Static

import rich.console
import rich.markup

from .client import LLMClient
from .config import Config, load_config, save_config, HISTORY_PATH
from .evaluator import Evaluator
from .tokenizer import Tokenizer
from .widgets import TokenCounter, PromptEditor, ResponseViewer, HistoryList


class SendPrompt(Message):
    """Message to trigger send."""

class ResponseReceived(Message):
    def __init__(self, data: Dict[str, Any]):
        super().__init__()
        self.data = data


class PromptPlaygroundApp(App[Screen]):
    """Main TUI app."""

    TITLE = "LLM Prompt Playground"
    CSS_PATH = "app.tcss"  # Optional

    BINDINGS = [
        ("ctrl+s", "send_prompt", "Send"),
        ("ctrl+b", "toggle_ab", "A/B Mode"),
        ("ctrl+h", "show_history", "History"),
        ("ctrl+c", "edit_config", "Config"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.config = load_config()
        self.client = LLMClient(self.config)
        self.tokenizer = Tokenizer()
        self.system_prompt = "You are a helpful assistant."
        self.user_prompt = ""
        self.model = self.config.default_model
        self.ab_mode = False
        self.history: List[Dict] = []
        self.load_history()
        self.response_data = None

    def compose(self) -> ComposeResult:
        yield Header(show_clock=True)
        yield Footer()
        yield Container(
            Label("Model: " + self.model, id="model-label"),
            TokenCounter(id="tokens"),
            id="header-bar"
        )
        yield PromptEditor(id="editor")
        yield ResponseViewer(id="response")
        yield Button("Send", id="send", variant="primary")

    def on_mount(self) -> None:
        container = self.query_one("#header-bar")
        container.styles.dock = "top"
        self.query_one("#tokens").tokens = 0

    @work(exclusive=True)
    async def send_prompt_worker(self) -> None:
        """Async send."""
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": self.user_prompt},
        ]
        prompt_tokens = self.tokenizer.count_messages(messages[:-1])

        try:
            data = await self.client.chat(messages, self.model)
            resp_content = data["choices"][0]["message"]["content"]
            response_tokens = self.tokenizer.count(resp_content)
            scores = Evaluator.evaluate(resp_content, prompt_tokens, response_tokens)
            data.update({"scores": scores, "content": resp_content})
            self.post_message(ResponseReceived(data))
            self.save_history(messages, data)
        except Exception as e:
            self.post_message(ResponseReceived({"error": str(e)}))

    @on(Button.Pressed, "#send")
    def action_send_prompt(self) -> None:
        self.send_prompt_worker()

    @on(ResponseReceived)
    def on_response(self, msg: ResponseReceived) -> None:
        viewer = self.query_one(ResponseViewer)
        if "error" in msg.data:
            viewer.get_child_by_id("response-text").update(f"[red]Error: {msg.data['error']}")
        else:
            content = msg.data["content"]
            viewer.get_child_by_id("response-text").update(content)
            scores_text = " | ".join(f"{k}: {v}" for k, v in msg.data["scores"].items())
            viewer.get_child_by_id("scores").update(f"[green]Scores: {scores_text}")

    def save_history(self, messages: List[Dict], data: Dict[str, Any]) -> None:
        entry = {
            "timestamp": datetime.now().isoformat(),
            "messages": messages,
            "model": self.model,
            **data,
        }
        HISTORY_PATH.parent.mkdir(exist_ok=True)
        with open(HISTORY_PATH, "a") as f:
            f.write(json.dumps(entry) + "\n")

    def load_history(self) -> None:
        if HISTORY_PATH.exists():
            with open(HISTORY_PATH) as f:
                self.history = [json.loads(line) for line in f]

    def action_toggle_ab(self) -> None:
        self.ab_mode = not self.ab_mode
        # Toggle container
        note("A/B mode: " + ("ON" if self.ab_mode else "OFF"))

    def action_show_history(self) -> None:
        self.push_screen(HistoryScreen())

    async def on_key(self, event: events.Key) -> None:
        if event.key == "ctrl+q":
            self.exit()

    async def on_shutdown(self) -> None:
        await self.client.close()


class HistoryScreen(Screen):
    def compose(self) -> ComposeResult:
        yield HistoryList(id="history")
        yield Horizontal(
            Button("Load", id="load", variant="primary"),
            Button("Close", id="close", variant="error"),
        )

    @on(Button.Pressed)
    def on_button(self, event: Button.Pressed) -> None:
        if event.button.id == "close":
            self.pop_screen()
