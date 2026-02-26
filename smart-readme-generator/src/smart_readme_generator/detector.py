import json
import re
from pathlib import Path
from typing import Dict, List
from . import tomlkit  # Avoid circular

SIGNATURES: Dict[str, List[tuple[str, str]]] = {
    "python-fastapi": [
        ("pyproject.toml", "fastapi"),
        ("requirements.txt", "fastapi"),
        ("Pipfile", "fastapi"),
    ],
    "python-django": [
        ("pyproject.toml", "django"),
        ("requirements.txt", "django"),
    ],
    "python-flask": [
        ("pyproject.toml", "flask"),
        ("requirements.txt", "flask"),
    ],
    "python": [
        ("pyproject.toml", "poetry"),
        ("setup.py", "setuptools"),
        ("requirements.txt", "pip"),
        ("Pipfile", "pipfile"),
    ],
    "nextjs": [("package.json", "next")],
    "react": [("package.json", "react")],
    "vue": [("package.json", "vue")],
    "express": [("package.json", "express")],
    "nodejs": [("package.json", '"dependencies"')],
    "actix-web": [("Cargo.toml", "actix-web")],
    "rocket": [("Cargo.toml", "rocket")],
    "rust": [("Cargo.toml", "[package]")],
    "gin": [("go.mod", "github.com/gin-gonic/gin")],
    "go": [("go.mod", "module")],
    "flutter": [("pubspec.yaml", "flutter:")],
}

FEATURES_PER_STACK = {
    "python-fastapi": ["FastAPI web framework", "Auto OpenAPI docs", "Pydantic validation", "Async support"],
    "python-django": ["Django ORM", "Admin panel", "Full-featured backend"],
    "python-flask": ["Lightweight web framework", "Jinja templating"],
    "nextjs": ["Next.js SSR/SSG", "App Router", "React + TypeScript"],
    "react": ["React components", "Hooks & Context", "Modern UI"],
    "vue": ["Vue.js reactivity", "Composition API"],
    "express": ["Node.js Express server", "Middleware stack"],
    "actix-web": ["High-perf Rust web", "Actor model"],
    "rocket": ["Rust web framework", "Type-safe routes"],
    "gin": ["Go Gin router", "Zero alloc middleware"],
}

INSTALL_CMDS = {
    "python": """python -m venv venv\\nsource venv/bin/activate # Windows: venv\\\\Scripts\\\\activate\\npip install -r requirements.txt""",
    "nodejs": """npm ci\\n# or yarn install --frozen-lockfile""",
    "rust": """cargo build --release\\ncargo test""",
    "go": """go mod tidy\\ngo build ./...""",
    "flutter": """flutter pub get\\nflutter analyze""",
}

USAGE_EXAMPLES = {
    "python-fastapi": """from fastapi import FastAPI\\n\\napp = FastAPI()\\n\\n@app.get("/")\\ndef root(): return {\"message\": \"Hello World\"}\\""",
    "react": """import React from 'react';\\n\\nfunction App() {\\n  return <div>Hello World</div>;\\n}""",
    "rust": """#[tokio::main]\\nasync fn main() {\\n    println!(\"Hello, world!\");\\n}""",
    "go": """package main\\n\\nimport \"fmt\"\\n\\nfunc main() {\\n    fmt.Println(\"Hello World\")\\n}""",
}

BADGES = {
    "python": "[![Python](https://img.shields.io/badge/python-3.11%2B-blue.svg?logo=python&logoColor=white)](https://python.org)",
    "nodejs": "[![Node.js](https://img.shields.io/badge/node-20+-green.svg?logo=node.js&logoColor=white)](https://nodejs.org)",
    "rust": "[![Rust](https://img.shields.io/badge/rust-1.75%2B-orange.svg?logo=rust&logoColor=white)](https://rust-lang.org)",
    "go": "[![Go](https://img.shields.io/badge/go-1.22%2B-blue.svg?logo=go&logoColor=white)](https://go.dev)",
}


def detect_stacks(path: Path) -> List[str]:
    stacks = []
    for stack, sigs in SIGNATURES.items():
        matched = any(
            (path / fname).exists() and kw.lower() in (path / fname).read_text().lower()
            for fname, kw in sigs
        )
        if matched:
            stacks.append(stack)
    return stacks


def parse_metadata(path: Path) -> tuple[str | None, str | None]:
    parsers = [
        (path / "pyproject.toml", lambda p: _parse_toml(p, ["tool", "poetry"])),
        (path / "Cargo.toml", lambda p: _parse_toml(p, ["package"])),
        (path / "package.json", lambda p: json.loads(p.read_text())),
        (path / "go.mod", lambda p: {"name": re.search(r"^module\\s+([^\\s]+)", p.read_text(), re.M).group(1).rsplit("/", 1)[-1] if re.search(...) else None}),
    ]
    name, desc = None, None
    for fpath, parser in parsers:
        if fpath.exists():
            try:
                data = parser(fpath)
                name = name or data.get("name")
                desc = desc or data.get("description")
            except (json.JSONDecodeError, KeyError, AttributeError):
                continue
    return name, desc


def _parse_toml(path: Path, keys: List[str]) -> dict:
    data = tomlkit.parse(path.read_text()).value
    for k in keys:
        data = data.get(k, {})
    return {"name": data.get("name"), "description": data.get("description")}


def has_tests(path: Path) -> bool:
    return any(d.name in ("tests", "test") for d in path.iterdir() if d.is_dir())


def has_ci(path: Path) -> bool:
    return (path / ".github" / "workflows").exists()


def detect_project(path: Path) -> Dict:
    stacks = detect_stacks(path)
    name_raw, desc = parse_metadata(path)
    project_name = name_raw.replace("-", " ").title() if name_raw else path.name.title()
    description = desc or "A high-quality project leveraging modern tools and best practices."
    features = list({f for s in stacks for f in FEATURES_PER_STACK.get(s, [])})
    lang_base = next((s.split("-")[0] for s in stacks), "")
    badges = [BADGES.get(lang_base, "")]
    badges.append("[![MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)")

    return {
        "project_name": project_name,
        "description": description,
        "stacks": stacks,
        "features": features,
        "has_tests": has_tests(path),
        "has_ci": has_ci(path),
        "badges": badges,
        "install_cmds": {s: INSTALL_CMDS.get(s.split("-")[0], INSTALL_CMDS.get("python", "")) for s in stacks},
        "usage_examples": {s: USAGE_EXAMPLES.get(s, "# Add your usage example here") for s in stacks},
    }