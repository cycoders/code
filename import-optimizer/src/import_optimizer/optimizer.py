import libcst as cst
from typing import List

from .analyzer import get_provided_names

STDLIB_MODULES = {
    "abc",
    "argparse",
    "ast",
    "asyncio",
    "base64",
    "bisect",
    "builtins",
    "bz2",
    "calendar",
    "collections",
    "concurrent",
    "configparser",
    "contextlib",
    "contextvars",
    "copy",
    "csv",
    "dataclasses",
    "datetime",
    "decimal",
    "difflib",
    "dis",
    "distutils",
    "doctest",
    "email",
    "encodings",
    "enum",
    "errno",
    "faulthandler",
    "fcntl",
    "filecmp",
    "fnmatch",
    "fractions",
    "functools",
    "gc",
    "generic",
    "getopt",
    "getpass",
    "glob",
    "gzip",
    "hashlib",
    "heapq",
    "hmac",
    "html",
    "http",
    "imaplib",
    "importlib",
    "inspect",
    "io",
    "ipaddress",
    "itertools",
    "json",
    "keyword",
    "linecache",
    "locale",
    "logging",
    "lzma",
    "math",
    "mimetypes",
    "mmap",
    "multiprocessing",
    "numbers",
    "operator",
    "os",
    "pathlib",
    "pdb",
    "pickle",
    "platform",
    "plistlib",
    "pprint",
    "profile",
    "pstats",
    "queue",
    "random",
    "re",
    "reprlib",
    "resource",
    "runpy",
    "sched",
    "secrets",
    "select",
    "selectors",
    "shlex",
    "shutil",
    "signal",
    "site",
    "smtplib",
    "socket",
    "socketserver",
    "sqlite3",
    "ssl",
    "stat",
    "statistics",
    "string",
    "struct",
    "subprocess",
    "sys",
    "sysconfig",
    "tarfile",
    "tempfile",
    "textwrap",
    "threading",
    "time",
    "timeit",
    "traceback",
    "tracemalloc",
    "types",
    "typing",
    "unicodedata",
    "unittest",
    "urllib",
    "uuid",
    "warnings",
    "wave",
    "weakref",
    "webbrowser",
    "xml",
    "xmlrpc",
    "zipfile",
    "zipimport",
    "zlib",
}

GROUP_ORDER = {"future": 0, "stdlib": 1, "thirdparty": 2, "local": 3}


def classify(stmt: cst.Import | cst.ImportFrom) -> str:
    if isinstance(stmt, cst.ImportFrom) and stmt.module:
        mod_value = stmt.module.value
        if mod_value == "__future__":
            return "future"
        if stmt.relative:
            return "local"
        if mod_value in STDLIB_MODULES:
            return "stdlib"
        return "thirdparty"
    # Import
    if isinstance(stmt, cst.Import) and stmt.names:
        first_mod = stmt.names[0].name.value
        return "stdlib" if first_mod in STDLIB_MODULES else "thirdparty"
    return "thirdparty"


def get_module_key(stmt: cst.Import | cst.ImportFrom) -> str:
    if isinstance(stmt, cst.ImportFrom):
        mod_str = stmt.module.value if stmt.module else ""
        names = sorted(alias.evaluated_name for alias in stmt.names)
        return f"{mod_str}.{','.join(names)}"
    else:
        names = sorted(alias.name.value for alias in stmt.names)
        return ",".join(names)


def process_module(module: cst.Module) -> cst.Module:
    # Collect loaded names
    loaded_visitor = LoadedNamesVisitor()
    loaded_visitor.visit(module)
    loaded_names = loaded_visitor.loaded

    # Top-level imports only
    top_imports = [
        stmt for stmt in module.body if isinstance(stmt, (cst.Import, cst.ImportFrom))
    ]

    # Provided names per stmt
    provided = [(stmt, get_provided_names(stmt)) for stmt in top_imports]

    # Unused
    unused_stmts = [
        stmt
        for stmt, names in provided
        if names != {"__all__star__"} and not (names & loaded_names)
    ]

    # Kept
    kept_imports = [stmt for stmt in top_imports if stmt not in unused_stmts]

    # Sort by group then key
    def sort_key(stmt: cst.Import | cst.ImportFrom) -> tuple[int, str]:
        group = classify(stmt)
        return (GROUP_ORDER.get(group, 99), get_module_key(stmt))

    sorted_imports = sorted(kept_imports, key=sort_key)

    # Build imports body with blanks
    imports_body: List[cst.BaseStatement] = []
    prev_group: str | None = None
    for stmt in sorted_imports:
        curr_group = classify(stmt)
        if prev_group is not None and curr_group != prev_group:
            imports_body.append(cst.SimpleStatementLine(body=[]))
        imports_body.append(stmt)
        prev_group = curr_group

    # Non-import statements
    non_imports = [
        stmt for stmt in module.body if not isinstance(stmt, (cst.Import, cst.ImportFrom))
    ]

    # New module
    new_body = imports_body + non_imports
    return module.with_changes(body=new_body)