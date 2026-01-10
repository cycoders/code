import json
from typing import Any

from rich.console import Console
from rich.json import JSONRenderer
from rich.syntax import Syntax

_console = Console()

def format_payload(payload: Any) -> None:
    """Format and print payload (JSON preferred, fallback syntax/str)."""
    if isinstance(payload, str):
        # Try JSON
        try:
            data = json.loads(payload)
            JSONRenderer().render(_console, data, indent=2)
        except json.JSONDecodeError:
            # Syntax highlight as JSON/YAML guess
            syntax = "json" if '{' in payload[:100] else "yaml"
            _console.print(Syntax(payload, syntax, line_numbers=False, word_wrap=True))
    elif isinstance(payload, (dict, list)):
        JSONRenderer(indent=2).render(_console, payload)
    else:
        _console.print(repr(payload))

    _console.print()  # Spacer