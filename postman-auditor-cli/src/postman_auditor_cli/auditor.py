import re
from typing import List, Set, Tuple, Union, Optional
from urllib.parse import urlparse

from .models import Collection, Item, Request
from .issues import Issue


SECRETS_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|secret|token|password|pwd|pass)([\\s=:]+|['\"])?([^'\"\\s,;:]{10,})['\"]?", re.IGNORECASE),
    re.compile(r"Bearer\\s+([a-zA-Z0-9_-]{20,})"),
    re.compile(r"sk-[a-zA-Z0-9]{48,}"),
    re.compile(r"AKIA[0-9A-Z]{16}"),
    re.compile(r"(?i)aws[_-]?access[_-]?key[_-]?id"),
]


_VAR_PATTERN = re.compile(r'\{\{([^}]+)\}\}')


class Auditor:
    @staticmethod
    def extract_vars(text: Optional[str]) -> Set[str]:
        if not text:
            return set()
        return {m.group(1).strip() for m in _VAR_PATTERN.finditer(text)}

    @staticmethod
    def scan_secrets_request(req: Request, path: List[str]) -> List[Issue):
        issues = []
        # URL
        for pat in SECRETS_PATTERNS:
            if pat.search(req.url.raw):
                issues.append(Issue("error", "secret-url", "Potential secret in URL", path + ["url"], "Use {{var}} instead"))
        # Headers
        for header in req.header or []:
            for pat in SECRETS_PATTERNS:
                if pat.search(header.value):
                    issues.append(Issue("error", "secret-header", f"Potential secret in header '{header.key}'", path + [f"header.{header.key}"], "Use {{var}}"))
        # Body
        if req.body and req.body.mode == "raw" and req.body.raw:
            for pat in SECRETS_PATTERNS:
                if pat.search(req.body.raw):
                    issues.append(Issue("error", "secret-body", "Potential secret in body", path + ["body"], "Use {{var}}"))
        return issues

    @staticmethod
    def scan_secrets_tree(tree: Union[Collection, Item], path: List[str]) -> List[Issue]:
        issues = []
        # Variables
        for var in getattr(tree, 'variable', []):
            if var.value:
                for pat in SECRETS_PATTERNS:
                    if pat.search(var.value):
                        issues.append(Issue("warning", "secret-var", f"Potential secret in var '{var.key}' value", path + [f"variable.{var.key}.value"], "Use external env"))
        # Request
        if isinstance(tree, Item) and tree.request:
            issues.extend(Auditor.scan_secrets_request(tree.request, path))
        # Children
        for child in getattr(tree, 'item', []):
            issues.extend(Auditor.scan_secrets_tree(child, path + [child.name]))
        return issues

    @staticmethod
    def analyze_variables_tree(tree: Union[Collection, Item], path: List[str]) -> Tuple[Set[str], List[Issue]]:
        local_vars = {v.key for v in getattr(tree, 'variable', [])}
        used_self = set()
        issues = []
        # Self request
        if isinstance(tree, Item) and tree.request:
            used_self |= Auditor.extract_vars(tree.request.url.raw)
            if tree.request.header:
                used_self |= {v for h in tree.request.header for v in Auditor.extract_vars(h.value)}
            if tree.request.body and tree.request.body.raw:
                used_self |= Auditor.extract_vars(tree.request.body.raw)
        # Children
        child_used = set()
        for child in getattr(tree, 'item', []):
            child_used_set, child_issues = Auditor.analyze_variables_tree(child, path + [child.name])
            issues.extend(child_issues)
            child_used |= child_used_set
        all_used = used_self | child_used
        unused = local_vars - all_used
        for var_name in unused:
            issues.append(Issue("warning", "unused-var", f"Variable '{var_name}' defined but unused in scope", path, "Remove or check usage"))
        return all_used, issues

    @staticmethod
    def check_duplicates(items: List[Item], path: List[str], issues: List[Issue]):
        if not items:
            return
        from collections import Counter
        names = [item.name for item in items]
        count = Counter(names)
        for name, cnt in count.items():
            if cnt > 1:
                issues.append(Issue("warning", "duplicate-name", f"'{name}' duplicated {cnt} times", path))
        for item in items:
            Auditor.check_duplicates(item.item or [], path + [item.name], issues)

    @staticmethod
    def check_descriptions_auth_urls(items: List[Item], path: List[str], issues: List[Issue]):
        for item in items:
            item_path = path + [item.name]
            # Description
            if item.item and len(item.item) > 1 and not item.description:
                issues.append(Issue("warning", "no-folder-desc", "Folder missing description", item_path, "Add overview of endpoints"))
            if item.request and not item.description:
                issues.append(Issue("info", "no-req-desc", "Request missing description", item_path, "Add purpose/expected response"))
            # Auth
            if item.request and item.auth is None:
                issues.append(Issue("warning", "no-auth", "Request missing auth config", item_path, "Set or inherit from parent"))
            # URL
            if item.request:
                try:
                    parsed = urlparse(item.request.url.raw)
                    if not parsed.scheme or not parsed.netloc:
                        issues.append(Issue("error", "invalid-url", "Invalid URL (no scheme/netloc)", item_path + ["url"]))
                except Exception:
                    issues.append(Issue("error", "invalid-url", "Unparseable URL", item_path + ["url"]))
            # Recurse
            if item.item:
                Auditor.check_descriptions_auth_urls(item.item, item_path, issues)

    @classmethod
    def audit(cls, collection: Collection) -> List[Issue]:
        issues: List[Issue] = []
        # Secrets
        issues.extend(cls.scan_secrets_tree(collection, []))
        # Variables
        _, var_issues = cls.analyze_variables_tree(collection, [])
        issues.extend(var_issues)
        # Duplicates
        cls.check_duplicates(collection.item, [], issues)
        # Desc/auth/URLs
        cls.check_descriptions_auth_urls(collection.item, [], issues)
        return issues
