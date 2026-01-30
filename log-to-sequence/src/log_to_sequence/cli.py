import base64
import webbrowser
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.markdown import Markdown

import log_to_sequence.models as models
from log_to_sequence import parser, builder, renderer, utils

app = typer.Typer(help="Generate Mermaid sequence diagrams from structured logs.", no_args_is_help=True)
console = Console()

@app.command()
def generate(
    input_path: Path = typer.Argument(..., help="JSONL log file or directory"),
    config_path: Optional[Path] = typer.Option(None, "--config", help="YAML config path"),
    output_dir: Path = typer.Option("output", "--output", help="Output directory"),
    preview: bool = typer.Option(False, "--preview", help="Auto-open mermaid.live preview (single trace)"),
):
    """Parse logs and generate sequence diagrams."""

    config = utils.load_config(config_path)
    output_dir.mkdir(exist_ok=True, parents=True)

    if input_path.is_dir():
        jsonl_files = list(input_path.glob("*.jsonl")) + list(input_path.glob("*.jsonl.gz"))
    else:
        jsonl_files = [input_path]

    preview_url = None
    for fpath in jsonl_files:
        console.print(f"[blue]Processing[/]: {fpath.name}")
        traces = parser.parse_log_file(fpath, config)

        for trace_id, entries in traces.items():
            if not entries:
                continue

            roots = builder.build_spans(entries)
            mermaid_code = renderer.render_mermaid(roots, config.service_aliases)

            # Markdown with embedded Mermaid
            md_content = f"# Trace: {trace_id[:8]}...\n\n```mermaid\n{mermaid_code}\n```"

            stem = fpath.stem.replace(".gz", "")
            md_path = output_dir / f"{stem}_{trace_id[:12]}.md"
            md_path.write_text(md_content)

            mmd_path = output_dir / f"{stem}_{trace_id[:12]}.mmd"
            mmd_path.write_text(mermaid_code)

            console.print(f"  [green]✓[/] {md_path.name} (+ .mmd)")

            if preview and len(jsonl_files) == 1 and len(traces) == 1:
                b64 = base64.urlsafe_b64encode(mermaid_code.encode("utf-8")).decode("ascii")
                preview_url = f"https://mermaid.live/edit#{b64}"

    if preview_url:
        console.print(f"[bold blue]Preview:[/] {preview_url}")
        webbrowser.open(preview_url)


if __name__ == "__main__":
    app()