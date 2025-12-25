from typing import List

import rich.console

from .models import ClassInfo, Method


class MermaidGenerator:
    """Generates Mermaid classDiagram syntax."""

    def __init__(self, classes: List[ClassInfo], console: rich.console.Console):
        self.classes = classes
        self.console = console
        self.class_names = {cls.name for cls in classes}

    def generate(self) -> str:
        """Generate full Mermaid diagram string."""
        lines: List[str] = ["classDiagram", "    direction TB"]

        # Class definitions
        for cls in self.classes:
            lines.append(f"    class `{cls.name}` {{{")
            # Attributes
            for attr in sorted(cls.attributes):
                lines.append(f"        +{attr}")
            # Methods
            for meth in sorted(cls.methods, key=lambda m: m.name):
                prefix = "+"
                if meth.is_static:
                    prefix = "#"
                elif meth.is_classmethod:
                    prefix = "~"
                lines.append(f"        {prefix}{meth.name}(){{}}")
            lines.append("    }}")

        # Inheritance links
        unresolved = []
        for cls in self.classes:
            for base in cls.bases:
                if base in self.class_names:
                    lines.append(f"    `{cls.name}` <|-- `{base}` : \"extends\"")
                else:
                    unresolved.append((cls.name, base))
        if unresolved:
            self.console.print(
                f"[yellow]⚠️  Unresolved bases: {len(unresolved)} (e.g. builtins/external)"
            )

        # Name clashes check
        name_counts = {}
        for cls in self.classes:
            name_counts[cls.name] = name_counts.get(cls.name, 0) + 1
        clashes = [n for n, c in name_counts.items() if c > 1]
        if clashes:
            self.console.print(
                f"[yellow]⚠️  Name clashes: {', '.join(clashes[:5])}... (use --qualify in v2)"
            )

        return "\n".join(lines) + "\n"
