import json
import sys
from pathlib import Path
from typing import Optional

import typer
from google.protobuf import descriptor_pb2

import rich_click as richc
from rich import print as rprint

from proto_schema_diff import __version__
from . import parser, differ, rules, visualizer


richc.STYLE_HELPS = ""
app = typer.Typer(rich_markup_mode="rich")


@app.command()
def main(
    old: Path = typer.Argument(..., help="Old .proto dir or .pb file"),
    new: Path = typer.Argument(..., help="New .proto dir or .pb file"),
    html: Optional[Path] = typer.Option(None, "--html/-H", help="HTML report"),
    json_out: Optional[Path] = typer.Option(None, "--json/-j", help="JSON report"),
    fail_breaking: bool = typer.Option(False, "--fail-on-breaking", help="Exit 1 on breaking changes"),
    version: bool = typer.Option(False, "--version", help="Show version"),
) -> None:
    if version:
        rprint(f"proto-schema-diff {__version__}")
        raise typer.Exit()

    try:
        old_set = _parse_input(old)
        new_set = _parse_input(new)

        diffs = differ.diff_sets(old_set, new_set)

        visualizer.print_diff(diffs)

        if rules.has_breaking_changes(diffs):
            rprint("[bold red]🚨 BREAKING CHANGES DETECTED![/bold red]")
            if fail_breaking:
                raise typer.Exit(code=1)

        if json_out:
            visualizer.to_json(diffs, json_out)
            rprint(f"[green]JSON saved: {json_out}"[green])

        if html:
            html_content = visualizer.render_html(diffs)
            html.write_text(html_content)
            rprint(f"[green]HTML saved: {html}"[green])

    except FileNotFoundError as e:
        typer.secho(f"Path not found: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)
    except subprocess.CalledProcessError:
        typer.secho(
            "[red]protoc failed. Install: brew install protobuf (or apt)[/red]", fg=typer.colors.RED
        )
        raise typer.Exit(1)
    except Exception as e:
        typer.secho(f"Error: {e}", fg=typer.colors.RED)
        raise typer.Exit(1)


def _parse_input(path: Path) -> descriptor_pb2.FileDescriptorSet:
    if path.is_dir():
        return parser.parse_proto_dir(path)
    elif path.suffix == ".pb":
        return parser.parse_descriptor_pb(path)
    else:
        raise ValueError(f"Unsupported input: {path} (use dir/*.proto or .pb)")


if __name__ == "__main__":
    app()