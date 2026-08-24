import libcst as cst
from pathlib import Path
from typing import List, Dict

def analyze_project(root: str, config_path: str | None = None) -> List[Dict]:
    findings = []
    for py_file in Path(root).rglob('*.py'):
        if 'test' in str(py_file):
            continue
        module = cst.parse_module(py_file.read_text())
        # simplified visitor for demo
        findings.append({'function': 'example', 'location': str(py_file)})
    return findings