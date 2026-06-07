from pathlib import Path
from typing import List
from jinja2 import Environment, FileSystemLoader
from .rules import ALL_RULES

class Finding:
    def __init__(self, rule: str, file: str, line: int, message: str):
        self.rule, self.file, self.line, self.message = rule, file, line, message

def scan_directory(root: str, fix: bool = False) -> List[Finding]:
    env = Environment(loader=FileSystemLoader(root), autoescape=True)
    findings: List[Finding] = []
    for template_path in Path(root).rglob("*.j2"):
        source = template_path.read_text()
        ast = env.parse(source)
        for rule in ALL_RULES:
            findings.extend(rule(ast, str(template_path)))
    return findings