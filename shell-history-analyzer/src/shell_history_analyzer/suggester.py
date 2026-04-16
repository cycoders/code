from typing import List

from .types import AnalysisResult


COMMON_PATTERNS = {
    "git log --oneline --graph --all": "glga",
    "git status": "gs",
    "ls -la": "ll",
    "docker ps": "dps",
    "docker logs -f": "dlog",
}


def suggest_optimizations(result: AnalysisResult) -> List[str]:
    """Generate alias/function suggestions."""
    suggestions = []
    for line, count in result.repeated_lines[:20]:
        if len(line.split()) > 2 and count > 15:
            # Heuristic alias name
            words = line.split()
            alias = "".join(w[0] for w in words[:3])
            if alias in COMMON_PATTERNS:
                alias = COMMON_PATTERNS.get(line.strip(), alias)
            suggestions.append(f"alias {alias}='{line.strip()}'  # used {count}x")

    # Long cmds
    for e in result.long_commands[:5]:
        alias = e.words[0][:3] + "l"
        suggestions.append(f"alias {alias}='{e.full_line.strip()}'  # long cmd")

    return suggestions[:10]
