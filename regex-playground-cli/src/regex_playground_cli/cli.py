import json
import sys
from typing import Optional

import typer
from rich.console import Console
from rich.prompt import Prompt

from .core import RegexTester
from .ui import render_pattern, render_test_result, render_explanation

app = typer.Typer()
console = Console(file=sys.stdout)


@app.command()
def playground():
    """Interactive regex playground."""
    console.print("[bold green]🎯 Welcome to Regex Playground CLI![/]\n")
    history: list[RegexTester] = []
    text_history: list[str] = []

    while True:
        default_pat = history[-1].pattern if history else ""
        pat_input = Prompt.ask("[bold cyan]Pattern[/]", default=default_pat, console=console)
        if pat_input.lower() in ("q", "quit", "exit"):
            break

        try:
            tester = RegexTester.from_input(pat_input)
            history.append(tester)
            render_pattern(console, tester)
            render_explanation(console, tester)
        except ValueError as e:
            console.print(f"[bold red]❌ Error:[/] {e}")
            continue

        text_idx = len(text_history) - 1
        while True:
            default_text = text_history[text_idx] if text_history and text_idx >= 0 else ""
            text_input = Prompt.ask("[bold yellow]Test text[/]", default=default_text, console=console)

            if text_input.lower() in ("q", "quit", "b", "back"):
                break
            if text_input.lower() == "h":
                if not history:
                    console.print("[yellow]No history[/]")
                    continue
                for i, tester in enumerate(history):
                    console.print(f"[cyan]{i}:[/] {tester.pattern} ({tester.flags_str})")
                try:
                    idx_str = Prompt.ask("[green]Select index[/]", console=console)
                    idx = int(idx_str)
                    tester = history[idx]
                    render_pattern(console, tester)
                    render_explanation(console, tester)
                    continue
                except (ValueError, IndexError):
                    console.print("[red]Invalid index[/]")
                    continue

            text_history.append(text_input)
            matches = tester.test(text_input)
            render_test_result(console, text_input, matches)

    console.print("[bold green]👋 Bye![/]\n")


@app.command()
def explain(pattern_input: str):
    """Explain a regex pattern."""
    try:
        tester = RegexTester.from_input(pattern_input)
        render_explanation(console, tester)
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True, color=False)
        raise typer.Exit(code=1)


@app.command()
def test(
    pattern_input: str,
    input_file: Optional[typer.FileText] = typer.Option(None, "--file", "-f", help="File to test (line-by-line)"),
):
    """Batch test pattern on file lines (JSONL output)."""
    if not input_file:
        raise typer.BadParameter("--file is required")
    try:
        tester = RegexTester.from_input(pattern_input)
        for line_num, line in enumerate(input_file, 1):
            line = line.strip()
            if not line:
                continue
            matches = tester.test(line)
            match_data = [{"start": m.start, "end": m.end, "groups": list(m.groups)} for m in matches]
            output = {
                "line": line_num,
                "text": line,
                "num_matches": len(matches),
                "results": match_data,
            }
            json.dump(output, sys.stdout, ensure_ascii=False)
            sys.stdout.write("\n")
    except ValueError as e:
        typer.echo(f"Error: {e}", err=True, color=False)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()
