import libcst as cst
from pathlib import Path

def scan_project(root: str):
    results = []
    for py in Path(root).rglob('*.py'):
        if 'test' in str(py):
            continue
        tree = cst.parse_module(py.read_text())
        # simplified: collect top-level imports
        results.append(f"{py}: {len([n for n in cst.walk(tree) if isinstance(n, cst.Import)])} imports")
    return results