from pathlib import Path
import json
import tomllib
from collections import Counter, defaultdict
from typing import Dict, Set, List

def detect_languages(root: Path) -> Dict[str, int]:
    """Detect languages by file extension counts."""
    ext_counter = Counter()
    for path in root.rglob("*"):
        if path.is_file():
            ext_counter[path.suffix] += 1

    lang_map: Dict[str, str] = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".jsx": "javascript",
        ".tsx": "typescript",
        ".go": "go",
        ".rs": "rust",
        ".java": "java",
        ".kt": "kotlin",
        ".scala": "scala",
        ".cpp": "cplusplus",
        ".c": "c",
        ".h": "cheaders",
        ".php": "php",
        ".rb": "ruby",
        ".swift": "swift",
        ".dart": "dart",
        ".sh": "shell",
        ".bat": "batch",
        ".ps1": "powershell",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".xml": "xml",
        ".md": "markdown",
        ".html": "html",
        ".htm": "html",
        ".css": "css",
        ".scss": "scss",
        ".sql": "sql",
        ".dockerfile": "docker",
        ".dockerignore": "docker",
        ".gradle": "gradle",
        ".toml": "toml",
    }

    languages: Dict[str, int] = {}
    for ext, count in ext_counter.most_common():
        lang = lang_map.get(ext)
        if lang:
            languages[lang] = languages.get(lang, 0) + count

    return dict(sorted(languages.items(), key=lambda x: x[1], reverse=True))


def detect_frameworks(root: Path) -> Set[str]:
    """Detect frameworks by marker files and config parsing."""
    frameworks: Set[str] = set()

    # File-based markers
    markers = {
        "django": ["manage.py", "django/settings.py"],
        "flask": ["app.py", "wsgi.py"],
        "rails": ["config/routes.rb", "Gemfile"],
        "flutter": ["pubspec.yaml"],
        "gradle": ["build.gradle", "gradlew"],
        "cargo": ["Cargo.toml"],
    }
    for fw, mfiles in markers.items():
        if any(root.glob(f"**/{m}") for m in mfiles):
            frameworks.add(fw)

    # pyproject.toml (Poetry/Pipenv)
    for toml_path in root.glob("**/pyproject.toml"):
        try:
            with open(toml_path, "rb") as f:
                data = tomllib.load(f)
            tool = data.get("tool", {})
            deps = {
                **tool.get("poetry", {}).get("dependencies", {}),
                **tool.get("poetry", {}).get("dev-dependencies", {}),
            }
            if "fastapi" in deps:
                frameworks.add("fastapi")
            if "streamlit" in deps:
                frameworks.add("streamlit")
        except (tomllib.TOMLDecodeError, KeyError, TypeError):
            pass

    # package.json (npm/yarn)
    pkg_path = root / "package.json"
    if pkg_path.exists():
        try:
            with open(pkg_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            deps = {
                **data.get("dependencies", {}),
                **data.get("devDependencies", {}),
                **data.get("peerDependencies", {}),
            }
            keys_lower = [k.lower() for k in deps]
            if any(x in keys_lower for x in ["react"]):
                frameworks.add("react")
            if "next" in deps:
                frameworks.add("nextjs")
            if any(x in keys_lower for x in ["vue", "@vue"]):
                frameworks.add("vuejs")
            if any(x.startswith("@angular") for x in deps):
                frameworks.add("angular")
            if "svelte" in deps:
                frameworks.add("svelte")
            if "nuxt" in deps:
                frameworks.add("nuxtjs")
        except (json.JSONDecodeError, KeyError):
            pass

    return frameworks