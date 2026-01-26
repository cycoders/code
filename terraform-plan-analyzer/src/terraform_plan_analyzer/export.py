from pathlib import Path
from typing import Dict, Any, List
import markdown_it

#from terraform_plan_analyzer.summarizer import format_summary
#from terraform_plan_analyzer.table import changes_to_md_table  # simple


def changes_to_md_table(changes: List[Dict[str, Any]]) -> str:
    """Convert changes to Markdown table."""
    if not changes:
        return "| No changes |\n|-------------|",
    headers = ["Address", "Type", "Action", "Changes"]
    rows = []
    for change in changes[:20]:  # Limit
        action = change["change"]["actions"][0]
        after = change["change"].get("after", {})
        changes_str = ", ".join(list(after.keys())[:3])
        rows.append(f"| {change['address']} | {change['type']} | {action} | {changes_str} |")
    return "\n".join(["| " + " | ".join(headers) + " |"] + rows + ["|:---:|:---:|:---:|:---:|"])


def export_report(
    output: Path,
    summary: Dict[str, Any],
    changes: List[Dict[str, Any]],
    risks: List[str],
    fmt: str = "md",
):
    """Generate Markdown report."""
    content = f"""# Terraform Plan Report

## Summary
{format_summary(summary)}

## Changes
{changes_to_md_table(changes)}

## Risks
{"\n".join(risks) if risks else "None detected."}
    """
    output.write_text(content)
