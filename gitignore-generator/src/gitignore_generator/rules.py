from typing import Dict, List

COMMON_RULES: List[str] = [
    # OS
    ".DS_Store",
    "Thumbs.db",
    "$RECYCLE.BIN/",
    "*.swp",
    "*.bak",
    "*.tmp",
    "*.log",
    # IDE
    ".vscode/",
    ".idea/",
    ".code-workspace",
    "*.sublime-*",
    # Testing
    ".coverage",
    "coverage.xml",
    "htmlcov/",
    ".pytest_cache/",
    ".hypothesis/",
    # Temp
    "*~",
]

LANG_RULES: Dict[str, List[str]] = {
    "python": [
        "__pycache__/",
        "*.py[cod]",
        "*$py.class",
        "*.so",
        ".python-version",
        ".venv/",
        "venv/",
        "env/",
        "pip-log.txt",
        "pip-delete-this-directory.txt",
        ".mypy_cache/",
        ".dmypy.json",
        ".dmypy.jsonc",
        "Pipfile.lock",
    ],
    "javascript": [
        "node_modules/",
        "npm-debug.log*",
        "yarn-debug.log*",
        "yarn-error.log*",
    ],
    "typescript": [
        "*.tsbuildinfo",
    ],
    "go": [
        "go.work",
    ],
    "rust": [
        "target/",
    ],
    "java": [
        "*.class",
        "*.jar",
        "*.war",
        "*.nar",
        "*.ear",
        "out/",
    ],
    "kotlin": [],
    "scala": [
        "target/",
        "*.log",
    ],
    "cplusplus": [
        "build/",
        "Debug/",
        "Release/",
    ],
    "c": [],
    "php": [
        "/vendor/",
    ],
    "ruby": [
        "*.gem",
        "Gemfile.lock",
    ],
    "swift": [
        "build/",
        "DerivedData/",
    ],
    "dart": [
        "build/",
    ],
    "shell": [],
    "batch": [],
    "powershell": [],
    "yaml": [],
    "json": [],
    "xml": [],
    "markdown": [],
    "html": [
        "dist/",
    ],
    "css": [],
    "scss": [],
    "sql": [
        "*.db",
        "*.sqlite",
    ],
    "docker": [
        "Dockerfile.*",
    ],
    "gradle": [
        "build/",
        "!gradle/wrapper/gradle-wrapper.jar",
        "!**/src/main/**/build/",
    ],
    "toml": [],
}

FRAMEWORK_RULES: Dict[str, List[str]] = {
    "django": [
        "db.sqlite3",
        "media/",
        "staticfiles/",
    ],
    "flask": [
        "instance/",
        ".env",
    ],
    "fastapi": [
        ".env",
    ],
    "streamlit": [
        ".streamlit/",
    ],
    "react": [
        "build/",
        ".env.local",
        ".env.development.local",
        ".env.test.local",
        ".env.production.local",
    ],
    "nextjs": [
        ".next/",
        "next-env.d.ts",
        "out/",
        "standalone/",
    ],
    "vuejs": [
        "dist/",
    ],
    "angular": [
        "dist/",
    ],
    "svelte": [
        "build/",
        "dist/",
    ],
    "nuxtjs": [
        ".nuxt/",
    ],
    "rails": [
        "log/*",
        "tmp/*",
        "tmp/cache/*",
        "storage/*",
        "public/system/*",
    ],
    "flutter": [
        "build/",
        ".dart_tool/",
        "flutter_*.log",
    ],
}