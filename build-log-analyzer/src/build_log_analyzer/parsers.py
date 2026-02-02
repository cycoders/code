import json
import re
from pathlib import Path
from typing import List

from .models import LogSummary, Step

ERROR_PATTERNS = [
    re.compile(r"(?i)(error|failed|fatal|exception)"),
    re.compile(r"(?i)error\[E\\d+\?\]"),
]
WARN_PATTERNS = [re.compile(r"(?i)warn(?:ing)?")]


def detect_parser(content: str) -> str:
    """Detect log format from content."""
    content_lower = content.lower()
    if "docker build" in content_lower or "step " in content_lower:
        return "docker"
    if "cargo " in content_lower:
        return "cargo"
    if "npm " in content_lower or "yarn " in content_lower:
        return "npm"
    if "pip install" in content_lower:
        return "pip"
    if any(line.strip().startswith("{") for line in content.splitlines()[:100]):
        return "gha"
    return "generic"


def parse_log(filepath: Path, parser_type: str = "auto") -> LogSummary:
    """Parse log file into structured summary."""
    if not filepath.exists():
        raise FileNotFoundError(f"Log file not found: {filepath}")
    content = filepath.read_text(encoding="utf-8", errors="ignore")
    lines = content.splitlines()
    if parser_type == "auto":
        parser_type = detect_parser(content)
    summary = LogSummary(filename=str(filepath), parser_used=parser_type)
    if parser_type == "gha":
        parse_gha(lines, summary)
    elif parser_type == "docker":
        parse_docker(lines, summary)
    elif parser_type == "npm":
        parse_npm(lines, summary)
    elif parser_type == "cargo":
        parse_cargo(lines, summary)
    elif parser_type == "pip":
        parse_pip(lines, summary)
    else:
        parse_generic(lines, summary)
    return summary


def parse_generic(lines: List[str], summary: LogSummary) -> None:
    """Generic parser: heuristic timings, error counts."""
    total_errors = 0
    total_warnings = 0
    time_sum = 0.0
    time_pat = re.compile(r"(\d+(?:\.\d+)?)\s*([smh])")
    for line in lines:
        if any(p.search(line) for p in ERROR_PATTERNS):
            total_errors += 1
        if any(p.search(line) for p in WARN_PATTERNS):
            total_warnings += 1
        if m := time_pat.search(line):
            val = float(m.group(1))
            unit = m.group(2)[0].lower()
            mult = {"s": 1, "m": 60, "h": 3600}.get(unit, 1)
            time_sum += val * mult
    summary.total_duration = time_sum if time_sum > 0 else None
    summary.total_errors = total_errors
    summary.total_warnings = total_warnings


def parse_docker(lines: List[str], summary: LogSummary) -> None:
    """Parse Docker build logs."""
    step_pat = re.compile(
        r"Step (?P<num>\d+)/ (?P<total>\d+) : (?P<name>[^\(]+) \((?P<dur>\d+(?:\.\d+)?)s?\)"
    )
    current_step: Optional[Step] = None
    current_errors: List[str] = []
    current_warnings: List[str] = []
    total_dur = 0.0
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()
        if m := step_pat.search(line_stripped):
            # Save previous step
            if current_step:
                current_step.errors = current_errors[:]
                current_step.warnings = current_warnings[:]
                summary.steps.append(current_step)
            gd = m.groupdict()
            current_step = Step(
                name=gd["name"].strip(),
                duration=float(gd["dur"]),
                status="success",
                start_line=i,
            )
            total_dur += current_step.duration or 0
            current_errors = []
            current_warnings = []
        elif any(p.search(line) for p in ERROR_PATTERNS):
            summary.total_errors += 1
            if current_step:
                current_errors.append(line_stripped)
        elif any(p.search(line) for p in WARN_PATTERNS):
            summary.total_warnings += 1
            if current_step:
                current_warnings.append(line_stripped)
    if current_step:
        current_step.errors = current_errors
        current_step.warnings = current_warnings
        summary.steps.append(current_step)
    summary.total_duration = total_dur


def parse_npm(lines: List[str], summary: LogSummary) -> None:
    """Parse npm/yarn logs."""
    time_pat = re.compile(r"(?:done in |)(?P<dur>\d+(?:\.\d+)?)s")
    dur_sum = 0.0
    summary.total_errors = sum(1 for line in lines if any(p.search(line) for p in ERROR_PATTERNS))
    summary.total_warnings = sum(1 for line in lines if any(p.search(line) for p in WARN_PATTERNS))
    for line in lines:
        if m := time_pat.search(line):
            dur_sum += float(m.group("dur"))
    summary.total_duration = dur_sum if dur_sum > 0 else None
    if dur_sum > 0:
        summary.steps.append(Step(name="npm/yarn", duration=dur_sum))


def parse_cargo(lines: List[str], summary: LogSummary) -> None:
    """Parse Cargo build logs."""
    time_pat = re.compile(r"Finished (.*?) target\(s\) in (?P<dur>\d+(?:\.\d+)?)s")
    summary.total_errors = sum(1 for line in lines if re.search(r"error\[E?\d*\]", line, re.I))
    summary.total_warnings = sum(1 for line in lines if "warning:" in line.lower())
    for line in lines:
        if m := time_pat.search(line):
            mode = m.group(1).strip("[] ")
            dur = float(m.group("dur"))
            summary.steps.append(Step(name=f"cargo {mode}", duration=dur))
            summary.total_duration = dur


def parse_pip(lines: List[str], summary: LogSummary) -> None:
    """Parse pip install logs."""
    installs = sum(1 for line in lines if "Successfully installed" in line)
    summary.total_errors = sum(1 for line in lines if "ERROR:" in line)
    status = "success" if summary.total_errors == 0 else "failure"
    summary.steps.append(Step(name=f"pip ({installs} pkgs)", status=status))
    summary.total_duration = None  # pip lacks total timing


def parse_gha(lines: List[str], summary: LogSummary) -> None:
    """Parse GitHub Actions JSONL logs."""
    total_errors = 0
    total_warnings = 0
    for line in lines:
        try:
            data = json.loads(line)
            msg = data.get("message", "")
            if "error" in msg.lower():
                total_errors += 1
            if "warning" in msg.lower():
                total_warnings += 1
        except json.JSONDecodeError:
            pass
    summary.total_errors = total_errors
    summary.total_warnings = total_warnings
    # Steps harder without full event log; fallback
    parse_generic(lines, summary)