from typing import Any, Dict, List, Union
import json
from pathlib import Path
from rich.table import Table
from rich.text import Text

from graphql_linter_cli.rules import RULE_DETAILS


class Reporter:
    def __init__(self, issues: List[Dict[str, Any]]):
        self.issues = issues

    def generate(self, fmt: str) -> Union[str, Table]:
        if fmt == "json":
            return json.dumps(self.issues, indent=2)
        elif fmt == "yaml":  # Requires pyyaml, omitted for zero deps
            raise NotImplementedError("YAML requires 'pyyaml'; install with extras")
        else:
            return self._build_table()

    def _build_table(self) -> Table:
        table = Table(title="Issues", show_header=True, box=None, expand=True)
        table.add_column("Severity", style="bold magenta")
        table.add_column("Rule")
        table.add_column("Path")
        table.add_column("Message")
        table.add_column("Fix")

        for issue in self.issues:
            sev = issue["severity"].upper()
            sev_style = {
                "error": "bold red",
                "warning": "bold yellow",
                "info": "bold cyan",
            }.get(sev.lower(), "")
            rule_name = issue["rule"]
            rule_detail = RULE_DETAILS.get(rule_name, {}).get("short", rule_name)
            path = issue["path"]
            msg = Text(issue["message"])
            fix = Text(issue.get("fix", "")) if issue.get("fix") else ""
            table.add_row(
                Text(sev, style=sev_style),
                rule_detail,
                path,
                str(msg),
                str(fix),
            )
        return table