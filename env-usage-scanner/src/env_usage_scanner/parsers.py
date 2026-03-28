import re
import yaml
from pathlib import Path
from typing import List, Dict, Any

from .models import Usage


# Language-specific regex patterns for env var detection
# Each pattern captures (var_name, snippet)
PATTERNS: Dict[str, List[re.Pattern]] = {
    "python": [
        re.compile(r"os\.(?:getenv|environ(?:\.get)?)\s*\(\s*['\"]([A-Z_][A-Z0-9_]*)['\"]", re.IGNORECASE),
        re.compile(r"os\.?environ\s*\[\s*['\"]([A-Z_][A-Z0-9_]*)['\"]\s*\]", re.IGNORECASE),
    ],
    "javascript": [
        re.compile(r"process\.env(?:\[['\"]([A-Z_][A-Z0-9_]*)['\"]\]|\.([A-Z_][A-Z0-9_]*) )", re.IGNORECASE),
    ],
    "go": [
        re.compile(r"os\.Getenv\(\s*['\"]([A-Z_][A-Z0-9_]*)['\"]\s*\)", re.IGNORECASE),
    ],
    "shell": [
        re.compile(r"\$\{?([A-Z_][A-Z0-9_]*)\}?") ,
    ],
    "dockerfile": [
        re.compile(r"^(?:ENV|ARG)\s+([A-Z_][A-Z0-9_]*)\b", re.IGNORECASE),
    ],
}


COMPOSE_ENV_KEYS = {'environment'}


def parse_python_js_go_shell_docker(file_path: Path, lang: str, content: str) -> List[Usage]:
    """Parse common langs with regex."""
    usages = []
    lines = content.splitlines()
    patterns = PATTERNS.get(lang, [])

    for i, line in enumerate(lines, 1):
        snippet = line.strip()[:80] + "..." if len(line.strip()) > 80 else line.strip()
        for pat in patterns:
            match = pat.search(line)
            if match:
                var_name = match.group(1) or match.group(2)
                if var_name:
                    usages.append(Usage(file_path, i, var_name, snippet, lang))
    return usages


def parse_compose(file_path: Path, content: str) -> List[Usage]:
    """Parse docker-compose.yml environment sections."""
    usages = []
    try:
        data = yaml.safe_load(content)
        def find_env(node: Any, path: str = ""):
            if isinstance(node, dict):
                for k, v in node.items():
                    full_path = f"{path}.{k}" if path else k
                    if k in COMPOSE_ENV_KEYS:
                        if isinstance(v, dict):
                            for var in v:
                                usages.append(Usage(file_path, 0, var, str(v), "compose"))
                        elif isinstance(v, list):
                            for var in v:
                                usages.append(Usage(file_path, 0, var, str(var), "compose"))
                    else:
                        find_env(v, full_path)
            elif isinstance(node, list):
                for item in node:
                    find_env(item, path)
        find_env(data)
    except yaml.YAMLError:
        pass  # Ignore invalid YAML
    return usages


def parse_file(file_path: Path, lang: str) -> List[Usage]:
    """Dispatch to appropriate parser."""
    try:
        content = file_path.read_text(encoding='utf-8', errors='ignore')
    except Exception:
        return []

    if lang == "compose":
        return parse_compose(file_path, content)
    else:
        return parse_python_js_go_shell_docker(file_path, lang, content)
