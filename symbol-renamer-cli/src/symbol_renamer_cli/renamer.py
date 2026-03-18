import libcst as cst
from pathlib import Path
from typing import Optional

from rich.console import Console

from .diff_utils import show_preview


class Renamer(cst.CSTTransformer):
    """CST transformer to rename matching Name nodes."""

    def __init__(self, old_name: str, new_name: str) -> None:
        self.old_name = old_name
        self.new_name = new_name
        self.changes: int = 0

    def leave_Name(
        self, original_node: cst.Name, updated_node: cst.Name
    ) -> cst.Name:
        if original_node.value == self.old_name:
            self.changes += 1
            return original_node.with_changes(value=self.new_name)
        return updated_node


def process_file(
    file_path: Path,
    old_name: str,
    new_name: str,
    console: Console,
    preview: bool = False,
    dry_run: bool = False,
    output_dir: Optional[str] = None,
    inplace: bool = False,
    root: Optional[Path] = None,
) -> int:
    """Process a single file: transform, preview/apply."""
    try:
        code = file_path.read_text(encoding="utf-8")
    except OSError:
        console.print(f"[red]Cannot read {file_path}[/]", err=True)
        return 0

    try:
        tree = cst.parse_module(code)
    except cst.ParserSyntaxError as err:
        console.print(f"[yellow]Skipping {file_path}: syntax error at {err}[/]", err=True)
        return 0

    transformer = Renamer(old_name, new_name)
    new_tree = tree.visit(transformer)
    new_code = new_tree.code

    if new_code == code:
        return 0

    changes = transformer.changes

    if preview:
        show_preview(code, new_code, file_path, console)

    if output_dir and root:
        rel_path = file_path.relative_to(root)
        out_path = Path(output_dir) / rel_path
        if dry_run:
            console.print(f"[blue]DRY-RUN: Would write to {out_path} ({changes} changes)[/]"))
        else:
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(new_code, encoding="utf-8")
            console.print(f"[green]Wrote {out_path} ({changes} changes)[/]"))
    elif inplace:
        if dry_run:
            console.print(f"[blue]DRY-RUN: Would rename {file_path} ({changes} changes)[/]"))
        else:
            backup = file_path.with_suffix(".bak")
            file_path.rename(backup)
            file_path.write_text(new_code, encoding="utf-8")
            console.print(f"[green]{file_path} renamed (backup: {backup}, {changes} changes)[/]"))
    else:
        if not dry_run:
            console.print("[yellow]Specify --output-dir or --inplace to apply.[/]"))

    return changes