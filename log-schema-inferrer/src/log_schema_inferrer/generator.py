import json
from pathlib import Path

def generate_parser(schema: dict, output_dir: str):
    """Generate production-ready parser module."""
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    code = _build_parser_code(schema)
    (Path(output_dir) / "generated_parser.py").write_text(code)

def _build_parser_code(schema):
    return """import re
from datetime import datetime

def parse_line(line: str):
    result = {}
    # auto-generated field extraction
    for field, meta in """ + json.dumps(schema["fields"]) + """.items():
        if field == "ts":
            result[field] = datetime.fromisoformat(line[:19])
        else:
            result[field] = line
    return result
"""