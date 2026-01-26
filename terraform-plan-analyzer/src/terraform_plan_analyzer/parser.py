from rich.console import Console
console = Console()

# Append to existing parser.py
def get_action(change: Dict[str, Any]) -> str:
    """Get primary action from change.actions."""
    actions = change["change"]["actions"]
    if not actions:
        return "no-op"
    if len(actions) == 1:
        return actions[0]
    return ",".join(sorted(actions))
