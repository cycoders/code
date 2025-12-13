from typing import List, Dict, Any

from .parser import Instruction


def analyze(instructions: List[Instruction]) -> Dict[str, Any]:
    """
    Analyze Dockerfile for optimization opportunities.

    Returns issues, savings estimate, stats.
    """
    issues = []
    potential_savings_mb = 0
    num_layers = len(instructions)
    runs = [i for i in instructions if i.command == "RUN"]
    num_runs = len(runs)

    # High RUN count → combine layers
    if num_runs > 3:
        savings = max(0, (num_runs - 2) * 20)
        potential_savings_mb += savings
        issues.append(
            f"Multiple RUNs ({num_runs}): combine to reduce layers by {num_runs-1}, "
            f"saving ~{savings}MB"
        )

    # Cache bust: COPY after installs
    copies = [i for i in instructions if i.command in ("COPY", "ADD")]
    install_keywords = [
        "apt-get install",
        "yum install",
        "pip install",
        "npm install",
        "yarn install",
        "apk add",
        "go mod download",
    ]
    for copy in copies:
        prior_runs = [
            i for i in instructions
            if i.line_number < copy.line_number and i.command == "RUN"
        ]
        if any(
            any(kw in r.args.lower() for kw in install_keywords) for r in prior_runs
        ):
            issues.append(
                f"Cache bust risk: {copy.command} (line {copy.line_number}) "
                "after install RUNs"
            )

    # Separate apt update/install
    apt_updates = [r for r in runs if "apt-get update" in r.args.lower()]
    apt_installs = [
        r for r in runs if "apt-get install" in r.args.lower() and r not in apt_updates
    ]
    if apt_updates and apt_installs:
        issues.append("Combine 'apt-get update' + 'install' to avoid stale cache")

    # Multi-stage
    froms = [i for i in instructions if i.command == "FROM"]
    if len(froms) > 1:
        issues.append(f"Multi-stage ({len(froms)} FROMs): minimize cross-stage COPY")

    return {
        "issues": issues,
        "potential_savings_mb": potential_savings_mb,
        "num_layers": num_layers,
        "num_runs": num_runs,
    }
