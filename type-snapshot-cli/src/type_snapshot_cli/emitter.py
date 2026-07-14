from pathlib import Path

def emit_patch(hints: Dict[str, str], out: Path):
    lines = ["# type: ignore[override]  # auto-generated snapshot\n"]
    for key, hint in hints.items():
        lines.append(f"# {key}: {hint}\n")
    out.write_text("".join(lines))