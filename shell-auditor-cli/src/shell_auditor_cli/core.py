import bashlex
from pathlib import Path
from typing import List

from .types import AuditResult, Issue
from .config import load_config


def get_shebang(text: str) -> str:
    if not text.strip():
        return ""
    first_line = text.splitlines()[0].strip()
    if first_line.startswith("#!"):
        return first_line[2:].strip()
    return ""


def parse_script(text: str) -> List:
    return bashlex.parse(text)


def check_tree(
    nodes: List, path: Path, shebang: str, skip_rules: set
) -> List[Issue]:
    issues = []

    def walk(node):
        # SEC001: eval
        if (
            hasattr(node, "parts")
            and node.parts
            and hasattr(node.parts[0], "word")
            and node.parts[0].word.strip() == "eval"
        ):
            rule_id = "SEC001"
            if rule_id not in skip_rules:
                issues.append(
                    Issue(
                        rule_id,
                        getattr(node, "row", 0) + 1,
                        getattr(node, "col", 0),
                        "Avoid 'eval' due to arbitrary code execution risk",
                        "critical",
                    )
                )

        # SEC002: rm * without -i
        if (
            hasattr(node, "parts")
            and node.parts
            and hasattr(node.parts[0], "word")
            and node.parts[0].word.strip() == "rm"
        ):
            args_str = " ".join(
                [p.word for p in node.parts[1:] if hasattr(p, "word")]
            )
            if "*" in args_str and "-i" not in args_str:
                rule_id = "SEC002"
                if rule_id not in skip_rules:
                    fix = f"rm -i {args_str}"
                    issues.append(
                        Issue(
                            rule_id,
                            getattr(node, "row", 0) + 1,
                            0,
                            "Use 'rm -i' for interactive confirmation with globs",
                            "high",
                            fix,
                        )
                    )

        # PERF001: cat | grep/head/etc
        if (
            hasattr(node, "parts")
            and len(node.parts) == 2
            and hasattr(node, "__class__")
            and "Pipeline" in str(node.__class__.__name__)
        ):
            left, right = node.parts
            if (
                hasattr(left, "parts")
                and left.parts
                and left.parts[0].word.strip() == "cat"
                and len(left.parts) == 2
                and hasattr(left.parts[1], "word")
                and hasattr(right, "parts")
                and right.parts
                and right.parts[0].word.strip() in ["grep", "head", "tail", "awk", "sed"]
            ):
                file_arg = left.parts[1].word.strip()
                right_cmd = right.parts[0].word.strip()
                right_args = [
                    p.word.strip() for p in right.parts[1:] if hasattr(p, "word")
                ]
                new_cmd = (
                    f"{right_cmd} {' '.join(right_args)} {file_arg}"
                    if right_args
                    else f"{right_cmd} {file_arg}"
                )
                rule_id = "PERF001"
                if rule_id not in skip_rules:
                    issues.append(
                        Issue(
                            rule_id,
                            getattr(node, "row", 0) + 1,
                            0,
                            f"Useless 'cat'; use '{new_cmd}' directly",
                            "medium",
                            new_cmd,
                        )
                    )

        # PERF002: for i in $(ls)
        if hasattr(node, "__class__") and "For" in str(node.__class__.__name__):
            if (
                hasattr(node, "list")
                and hasattr(node.list, "command")
                and hasattr(node.list.command, "parts")
                and node.list.command.parts
                and node.list.command.parts[0].word.strip() == "ls"
            ):
                rule_id = "PERF002"
                if rule_id not in skip_rules:
                    issues.append(
                        Issue(
                            rule_id,
                            getattr(node, "row", 0) + 1,
                            0,
                            "Avoid 'for i in $(ls)'; use 'for i in *' or 'find'",
                            "medium",
                        )
                    )

        # PORT001: [[ bashism
        if hasattr(node, "__class__") and "DoubleBracket" in str(node.__class__.__name__):
            rule_id = "PORT001"
            if rule_id not in skip_rules:
                issues.append(
                    Issue(
                        rule_id,
                        getattr(node, "row", 0) + 1,
                        0,
                        "'[[ ]]' is bashism; use '[ ]' for POSIX/sh compatibility",
                        "medium",
                    )
                )

        # Recurse children/parts
        if hasattr(node, "children"):
            for child in getattr(node, "children", []):
                walk(child)
        if hasattr(node, "parts"):
            for part in getattr(node, "parts", []):
                walk(part)

    for node in nodes:
        walk(node)

    # Shebang check (extra for PORT001 if sh)
    if shebang and "/bin/sh" in shebang and "/bash" not in shebang:
        has_bashism = any(i.rule_id == "PORT001" for i in issues)
        if not has_bashism:
            rule_id = "PORT001"
            if rule_id not in skip_rules:
                issues.append(
                    Issue(
                        rule_id,
                        1,
                        0,
                        "sh shebang detected with potential bashisms (scanned)",
                        "low",
                    )
                )

    return issues


def audit(path: Path, config: dict = None) -> AuditResult:
    config = config or load_config()
    skip_rules = set(config.get("audit", {}).get("skip_rules", []))

    text = path.read_text(encoding="utf-8")
    shebang = get_shebang(text)

    parse_errors = []
    issues = []
    try:
        nodes = parse_script(text)
        issues = check_tree(nodes, path, shebang, skip_rules)
    except Exception as e:
        parse_errors.append(str(e))

    return AuditResult(path, issues, parse_errors)