from collections import defaultdict
from typing import Dict, List

from .types import Commit


_HEADER = """# Changelog

All notable changes to this project will be documented in this file.

"""


class Renderer:
    """Changelog renderer."""

    @staticmethod
    def render(commits: List[Commit], config: Dict) -> str:
        """Render commits to Markdown."""
        type_to_section = config["type_to_section"]
        section_order = config["section_order"]

        sections: Dict[str, List[Commit]] = defaultdict(list)
        for commit in commits:
            section = type_to_section.get(commit.type_, "Other Changes")
            if commit.breaking:
                section = "Breaking Changes"
            sections[section].append(commit)

        lines = [_HEADER]

        for section_name in section_order:
            if section_name in sections:
                lines.extend(Renderer._render_section(section_name, sections[section_name]))

        if "Other Changes" in sections:
            lines.extend(Renderer._render_section("Other Changes", sections["Other Changes"]))

        if "Breaking Changes" in sections:
            lines.extend(Renderer._render_section("Breaking Changes", sections["Breaking Changes"]))

        return "".join(lines)

    @staticmethod
    def _render_section(title: str, commits: List[Commit]) -> List[str]:
        lines = [f"## {title}", "", "- " + "\n- ".join(Renderer._format_commit(c) for c in commits), "", "",]
        return lines

    @staticmethod
    def _format_commit(c: Commit) -> str:
        parts = [c.title]
        if c.scope:
            parts.append(f"({c.scope})")
        parts.append(f" [{c.sha[:8]}]")
        return "".join(parts)