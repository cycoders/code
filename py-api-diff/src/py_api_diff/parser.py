import ast
import os
import subprocess
from pathlib import Path
from typing import Iterator, Optional, Set

from .models import ApiElement, ArgSig


def get_git_root(cwd: str = ".") -> Path:
    """Get git repo root."""
    try:
        cmd = ["git", "rev-parse", "--show-toplevel"]
        out = subprocess.check_output(cmd, cwd=cwd, text=True, stderr=subprocess.DEVNULL).strip()
        return Path(out).resolve()
    except subprocess.CalledProcessError:
        raise RuntimeError("Not a git repository (or any of the parent directories)")


def get_py_files(root: Path, rev: Optional[str] = None) -> list[str]:
    """List all .py files in tree/rev."""
    if rev:
        try:
            cmd = ["git", "ls-tree", "-r", "--name-only", rev]
            out = subprocess.check_output(cmd, cwd=root, text=True, stderr=subprocess.DEVNULL).strip()
            return [line for line in out.splitlines() if line.endswith(".py")]
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Invalid rev '{rev}': {e}")
    else:
        return [p.relative_to(root).as_posix() for p in root.rglob("*.py")]


def get_file_content(relpath: str, root: Path, rev: Optional[str] = None) -> str:
    """Get file content from rev or filesystem."""
    if rev:
        try:
            cmd = ["git", "show", f"{rev}:{relpath}"]
            return subprocess.check_output(cmd, cwd=root, text=True, stderr=subprocess.DEVNULL)
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Failed to read {relpath}@{rev}: {e}")
    else:
        return (root / relpath).read_text(errors="ignore")


def parse_args(args_node: ast.arguments) -> tuple[ArgSig, ...]:
    """Parse args, skip 'self' for __init__."""
    sigs = []
    skip_self = False
    if args_node.args and args_node.args[0].arg == "self":
        skip_self = True
        start = 1
    else:
        start = 0
    for arg in args_node.args[start:]:
        sigs.append(ArgSig(arg.arg, arg.default is not None))
    return tuple(sigs)


def parse_py_file(content: str, modname: str) -> Iterator[ApiElement]:
    """Parse top-level public functions/classes."""
    try:
        tree = ast.parse(content, filename=modname)
    except SyntaxError:
        return  # Skip invalid

    for stmt in tree.body:
        if isinstance(stmt, ast.FunctionDef) and not stmt.name.startswith("_"):
            arg_sigs = parse_args(stmt.args)
            qualname = f"{modname}.{stmt.name}"
            yield ApiElement(qualname, "function", arg_sigs)
        elif isinstance(stmt, ast.ClassDef) and not stmt.name.startswith("_"):
            init_args = tuple()
            for body_stmt in stmt.body:
                if isinstance(body_stmt, ast.FunctionDef) and body_stmt.name == "__init__":
                    init_args = parse_args(body_stmt.args)
                    break
            qualname = f"{modname}.{stmt.name}"
            yield ApiElement(qualname, "class", init_args)


def parse_tree(root: Path, rev: Optional[str] = None) -> Set[ApiElement]:
    """Parse full tree/rev to public API set."""
    root = root.resolve()
    py_files = get_py_files(root, rev)
    apis: Set[ApiElement] = set()
    for relpath in py_files:
        content = get_file_content(relpath, root, rev)
        modname = relpath[:-3].replace(os.sep, ".").replace("./", "")
        apis.update(parse_py_file(content, modname))
    return apis