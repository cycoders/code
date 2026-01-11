import ast
import sys
import typer
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich import print as rprint

from .parser import ImportResolver, CallExtractor, find_function, find_class
from .writer import generate_test_code


app = typer.Typer(add_completion=False)
console = Console(file=sys.stderr)


@app.command(help="Generate pytest mocks for a function or method")
def generate(
    target: str = typer.Argument(..., help="file.py:function or file.py:Class.method"),
    output: Optional[typer.FileTextWrite] = typer.Option(
        None, "--output", "-o", help="Write to file (default: stdout)"
    ),
):
    """Auto-generate pytest mock test from static analysis."""
    try:
        path_str, obj_name = target.rsplit(":", 1)
        path = Path(path_str).resolve()
        if not path.is_file():
            raise typer.BadParameter(f"File not found: {path}")

        source = path.read_text(encoding="utf-8")
        tree = ast.parse(source, filename=str(path))

        resolver = ImportResolver()
        resolver.visit(tree)

        class_node = None
        func_node = None
        is_method = "." in obj_name

        if is_method:
            class_name, method_name = obj_name.split(".", 1)
            class_node = find_class(tree, class_name)
            if class_node:
                func_node = find_function(class_node, method_name)
        else:
            func_node = find_function(tree, obj_name)

        if not func_node:
            raise typer.BadParameter(f"Function/method '{obj_name}' not found in {path.name}")

        extractor = CallExtractor(resolver)
        extractor.visit(func_node)
        calls = extractor.external_calls

        module_name = path.stem.replace("-", "_").replace(".", "_")
        func_name = func_node.name
        class_name = class_node.name if class_node else None

        test_code = generate_test_code(module_name, func_name, calls, is_method, class_name)

        if output:
            output.write(test_code)
            output.flush()
        else:
            rprint(test_code)

    except ValueError as e:
        typer.echo(f"[red]Error:[/red] {e}", err=True)
        raise typer.Exit(code=1)
    except Exception:
        console.print_exception(show_locals=False)
        raise typer.Exit(code=1)


if __name__ == "__main__":
    app()