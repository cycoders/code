from typing import Dict, Any, List
from collections import Counter
from pathlib import Path
import tomllib
from git import GitCommandError

def load_config() -> Dict:
    """Load user config from ~/.config/commit-suggest-cli/config.toml"""
    from pathlib import Path
    config_dir = Path.home() / ".config" / "commit-suggest-cli"
    config_path = config_dir / "config.toml"
    if config_path.exists():
        with open(config_path, "rb") as f:
            config = tomllib.load(f)
        return config
    return {}

TYPES: Dict[str, List[str]] = {
    "feat": ["add", "new", "implement", "feature"],
    "fix": ["fix", "bug", "error", "issue"],
    "docs": ["doc", "document", "readme"],
    "style": ["style", "format", "lint"],
    "refactor": ["refactor", "rename", "restructure"],
    "perf": ["perf", "performance", "optimize", "speed"],
    "test": ["test"],
    "chore": ["chore", "update", "bump"],
    "ci": ["ci", "workflow", "github"],
    "revert": ["revert"],
}

# Apply config overrides
config = load_config()
types_config = config.get("types", {})
for typ, data in types_config.items():
    if isinstance(data, dict) and "keywords" in data:
        TYPES[typ] = data["keywords"]

def score_type(typ: str, lines: List[str]) -> int:
    """Score how well lines match type keywords."""
    return sum(1 for kw in TYPES[typ] if any(kw in line.lower() for line in lines))

def get_type(lines: List[str]) -> str:
    """Infer commit type from changed lines."""
    if not lines:
        return "chore"
    scores = {typ: score_type(typ, lines) for typ in TYPES}
    return max(scores, key=scores.get)

def get_scope(files: List[str]) -> str:
    """Infer scope from common directory."""
    if not files:
        return ""
    dirs = [Path(f).parts[-2] if len(Path(f).parts) > 1 else "root" for f in files]
    common = Counter(dirs).most_common(1)
    return common[0][0] if common else ""

def suggest_message(changes: Dict[str, Any]) -> str:
    """Generate full commit message."""
    files = changes["files"]
    adds = [l.strip() for l in changes["added_lines"]]
    rems = [l.strip() for l in changes["removed_lines"]]

    typ = get_type(adds + rems)
    scope = get_scope(files)
    scope_str = f"({scope})" if scope else ""

    # Smart subject
    add_cnt = len(adds)
    subject = f"{add_cnt} {'add' if add_cnt == 1 else 'adds'}{' and fixes' if rems else ''}"
    if scope:
        subject += f" in {scope}"

    # Use code snippets if possible
    clean_adds = [l for l in adds[:3] if not l.startswith("import ") and len(l) > 3]
    if clean_adds:
        subject = f"{' | '.join(clean_adds[:2]).capitalize()[:60]}"

    msg = f"{typ}{scope_str}: {subject}"

    # Body: files
    if files:
        msg += "\n\nFiles changed:\n"
        for f in files[:8]:
            msg += f"- {f}\n"
        if len(files) > 8:
            msg += f"- and {len(files)-8} more\n"

    return msg.strip()
