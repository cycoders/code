from typing import Dict, Optional
import re
from bs4 import BeautifulSoup
from pathlib import Path

from .types import Issue
from .config import Config
from .checks import CHECKS  # All check functions


class Auditor:
    """Core auditor class. Aggregates issues by ID."""

    def __init__(self, html: str, config_path: Optional[str] = None) -> None:
        self.original_html = html
        self.soup: BeautifulSoup = BeautifulSoup(html, 'lxml')
        self.config = Config(config_path)
        self.issues: Dict[str, Issue] = {}

    def _add_issue(self, issue: Issue) -> None:
        iid = issue.id
        if iid in self.issues:
            existing = self.issues[iid]
            existing.count += 1
            if issue.examples:
                existing.examples.append(issue.examples[0])
        else:
            self.issues[iid] = issue

    def audit(self) -> None:
        """Run all enabled checks."""
        for check_id, check_func in CHECKS.items():
            if check_id in self.config.disabled_checks:
                continue
            try:
                check_func(self)
            except Exception as e:
                self._add_issue(Issue(
                    id='internal-error',
                    wcag='N/A',
                    principle='Robust',
                    level='AAA',
                    severity='error',
                    description=f'Check {check_id} failed: {str(e)}',
                    impact='Low',
                    help='Report bug.',
                ))

    @property
    def issues_list(self) -> list[Issue]:
        return list(self.issues.values())

    def get_score(self) -> str:
        total = len(self.issues_list)
        if total == 0:
            return 'A'
        elif total <= 5:
            return 'B'
        elif total <= 15:
            return 'C'
        elif total <= 30:
            return 'D'
        else:
            return 'F'