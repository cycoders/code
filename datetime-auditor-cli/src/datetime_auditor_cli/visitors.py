import ast
from pathlib import Path

from .types import Issue


class DatetimeAuditor(ast.NodeVisitor):
    def __init__(self, filename: Path, source: str):
        self.filename = filename
        self.source = source
        self.issues: list[Issue] = []

    def visit_Call(self, node: ast.Call) -> Any:
        self._check_datetime_call(node)
        self.generic_visit(node)

    def _check_datetime_call(self, node: ast.Call) -> None:
        func = node.func

        # datetime.method(...)
        if isinstance(func, ast.Attribute) and isinstance(func.value, ast.Name) and func.value.id == "datetime":
            attr = func.attr
            if attr in ("now", "utcnow"):
                if not self._has_tz(node, base_args=0):
                    msg = f"Naive `datetime.{attr}()` call - specify `tz` parameter for timezone-aware datetime"
                    self._add_issue(node, msg)
            elif attr == "fromtimestamp":
                if not self._has_tz(node, base_args=1):
                    msg = "Naive `datetime.fromtimestamp()` - provide `tz` argument"
                    self._add_issue(node, msg)
            elif attr == "strptime":
                if not self._has_tz(node, base_args=2):
                    msg = "Potentially naive `datetime.strptime()` - consider `tz=None` kwarg"
                    self._add_issue(node, msg, severity="warning")

        # datetime(...)
        elif isinstance(func, ast.Name) and func.id == "datetime":
            has_tzinfo = any(kw.arg == "tzinfo" for kw in node.keywords)
            if not has_tzinfo:
                msg = "Naive `datetime(...)` constructor - specify `tzinfo` kwarg"
                self._add_issue(node, msg, severity="warning")

    def _has_tz(self, node: ast.Call, base_args: int) -> bool:
        # tz kwarg
        if any(kw.arg == "tz" for kw in node.keywords):
            return True
        # Extra positional arg as tz
        if len(node.args) > base_args:
            return True
        return False

    def _add_issue(self, node: ast.Call, msg: str, severity: str = "error") -> None:
        snippet = self._get_snippet(node)
        issue = Issue(
            self.filename,
            node.lineno,
            node.col_offset,
            msg,
            severity=severity,
            snippet=snippet,
        )
        self.issues.append(issue)

    def _get_snippet(self, node: ast.Call) -> str:
        try:
            lines = self.source.splitlines()
            start = node.lineno - 1
            end = getattr(node, "end_lineno", node.lineno + 1)
            snippet_lines = lines[start:end]
            snippet = "\n".join(snippet_lines).strip()
            if len(snippet) > 120:
                snippet = snippet[:120] + "..."
            return f"`{snippet}`"
        except:
            return ""