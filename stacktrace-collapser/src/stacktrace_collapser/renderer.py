import tempfile
import webbrowser
import os
from pathlib import Path
from typing import Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text
from rich_markup import RichMarkup
from jinja2 import Template
from .models import Frame

TEMPLATE_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Stacktrace Collapser</title>
    <style>
        body { font-family: -apple-system, BlinkMacSystemFont, sans-serif; max-width: 1000px; margin: 2em auto; }
        h1 { color: #dc2626; }
        details { margin: 0.5em 0; border-left: 4px solid #0ea5e9; padding-left: 1em; }
        summary { cursor: pointer; font-weight: 600; color: #0369a1; padding: 0.5em; }
        .frame-info { color: #64748b; font-family: monospace; }
        .count { color: #9ca3af; font-size: 0.9em; }
    </style>
</head>
<body>
    <h1>💥 Collapsed Stack Trace ({{ language | upper }})</h1>
    {% for frame in frames %}
    <details {{ 'open' if frame.count <= 1 else '' }}>
        <summary>
            {{ loop.index }}. <strong>{{ frame.func }}</strong>
            <span class="frame-info">({{ frame.short_file }}:{{ frame.line }}{% if frame.col %}:{{ frame.col }}{% endif %}}{% if frame.count > 1 %} <span class="count">(x{{ frame.count }})</span>{% endif %})</span>
        </summary>
        <div class="frame-info">{{ frame.file }}:{{ frame.line }}</div>
    </details>
    {% endfor %}
</body>
</html>
"""

template = Template(TEMPLATE_HTML)


def render_terminal(frames: list[Frame], language: str, console: Console):
    panel = Panel.fit(
        _build_frames_text(frames),
        title="[bold red]💥 Stack Trace ([cyan]{}[/cyan])".format(language.upper()),
        border_style="red",
    )
    console.print(panel)


def _build_frames_text(frames: list[Frame]) -> Text:
    text = Text()
    for i, frame in enumerate(frames, 1):
        short_file = "/".join(Path(frame.file).parts[-2:])
        loc = f"{short_file}:{frame.line}"
        if frame.col:
            loc += f":{frame.col}"
        count_str = f" [dim](x{frame.count})[/]" if frame.count > 1 else ""
        frame_text = f"{i}. [bold cyan]{frame.func}[/bold cyan] [magenta dim]{loc}[/magenta dim]{count_str}\n"
        text.append(frame_text, markup=True)
    return text


def render_html(frames: list[Frame], language: str) -> str:
    frame_data: list[Dict[str, Any]] = []
    for frame in frames:
        short_file = "/".join(Path(frame.file).parts[-2:])
        frame_data.append({
            "func": frame.func,
            "file": frame.file,
            "short_file": short_file,
            "line": frame.line,
            "col": frame.col,
            "count": frame.count,
        })
    return template.render(frames=frame_data, language=language)


def render_json(st: 'Stacktrace') -> str:
    return st.model_dump_json(indent=2)
