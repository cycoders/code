'''
Rich Typer CLI.
'''

import os
import sys
import typer
from pathlib import Path
from typing import List

import pydantic
from pydantic import Field, ValidationError

from rich.console import Console

from .scanner import scan_directory
from .generator import (
    generate_pydantic_model,
    generate_docs,
    generate_env_example,
)


app = typer.Typer(add_completion=False)
console = Console(file=sys.stderr)


def make_default_factory(var: str, typ: str):
    """Factory for Pydantic default_factory. Captures var/typ."""
    if typ == 'str':
        def df() -> str:
            return os.getenv(var, '')
        return df
    elif typ == 'int':
        def df() -> int:
            return int(os.getenv(var, '0'))
        return df
    elif typ == 'float':
        def df() -> float:
            return float(os.getenv(var, '0.0'))
        return df
    elif typ == 'bool':
        def df() -> bool:
            return os.getenv(var, 'false').lower() in ('true', '1', 'yes', 'on')
        return df
    else:
        def df() -> str:
            return os.getenv(var, '')
        return df


@app.command(help='Scan codebase for env vars, output JSON')
def scan(
    root: Path = typer.Argument(Path('.'), help='Root dir'),
    output: Path = typer.Option('vars.json', '--output', '-o'),
    exclude: List[str] = typer.Option([], '--exclude/-x'),
):
    data = scan_directory(root, exclude)
    output.write_text(json.dumps(data, indent=2))
    console.print(
        f'[bold green]Found {data["summary"]["total_vars"]} vars '
        f'in {data["summary"]["total_files"]} files → {output}',
        highlight=False,
    )


@app.command(help='Generate Pydantic schema + docs + .env.example')
def generate(
    root: Path = typer.Argument(Path('.'), help='Root dir'),
    schema: Path = typer.Option('env_schema.py', '--schema/-s'),
    docs: Path = typer.Option('ENV_VARS.md', '--docs/-d'),
    env_example: Path = typer.Option('.env.example', '--env-ex/-e'),
    exclude: List[str] = typer.Option([], '--exclude/-x'),
):
    data = scan_directory(root, exclude)
    schema.write_text(generate_pydantic_model(data))
    docs.write_text(generate_docs(data))
    env_example.write_text(generate_env_example(data))
    console.print(
        '[bold green]✅ Generated:\n'
        f'  📄 {schema}\n'
        f'  📋 {docs}\n'
        f'  .env {env_example}',
    )


@app.command(help='Validate os.environ against inferred schema')
def validate(
    root: Path = typer.Argument(Path('.'), help='Root dir'),
    strict: bool = typer.Option(False, '--strict', help='Fail on missing vars'),
    exclude: List[str] = typer.Option([], '--exclude/-x'),
):
    data = scan_directory(root, exclude)
    if not data['vars']:
        console.print('[bold yellow]No env vars found.')
        raise typer.Exit(code=1)

    fields = {}
    py_types = {'str': str, 'int': int, 'float': float, 'bool': bool}
    for var_name, info in data['vars'].items():
        typ_str = info['type']
        py_type = py_types.get(typ_str, str)
        fields[var_name] = (
            py_type,
            Field(default_factory=make_default_factory(var_name, typ_str)),
        )

    EnvDynamic = pydantic.create_model('EnvDynamic', **fields)

    env_subset = {k: v for k, v in os.environ.items() if k in fields}
    try:
        _ = EnvDynamic.model_validate(env_subset)
        console.print('[bold green]✅ All env vars validate!')

        if strict:
            missing = [v for v in data['vars'] if os.getenv(v) is None]
            if missing:
                console.print(f'[bold yellow]Missing: {", ".join(missing[:10])}...')
                raise typer.Exit(code=1)

    except ValidationError as exc:
        console.print('[bold red]❌ Errors:')
        for err in exc.errors():
            loc = '.'.join(str(l) for l in err['loc'])
            console.print(f'  [red]{loc}: {err["message"]}')
        raise typer.Exit(code=1)


if __name__ == '__main__':
    app()