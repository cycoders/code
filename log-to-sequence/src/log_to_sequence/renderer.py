from typing import List, Dict

import log_to_sequence.models as models
from log_to_sequence.utils import get_service_alias


def render_mermaid(roots: List[models.Span], aliases: Dict[str, str]) -> str:
    if not roots:
        return "sequenceDiagram\n    Note over : No spans"

    # Collect unique services
    services = set()
    def collect(span: models.Span):
        services.add(span.service)
        for child in span.children:
            collect(child)
    for root in roots:
        collect(root)

    service_aliases = {s: get_service_alias(s, aliases) for s in services}

    parts = ["sequenceDiagram"]

    # Participants, sorted alphabetically
    for service, alias in sorted(service_aliases.items()):
        parts.append(f"    participant {alias} as {service}")

    def render_span(span: models.Span, parent_alias: Optional[str] = None) -> List[str]:
        lines: List[str] = []
        my_alias = service_aliases[span.service]

        lines.append(f"    activate {my_alias}")
        if span.name != "unknown":
            lines.append(f"    Note over {my_alias}: {span.name}")

        for child in span.children:
            child_alias = service_aliases[child.service]
            if child_alias == my_alias:
                # Same service recursion
                lines.extend(render_span(child))
            else:
                # Cross-service call
                lines.append(f"    {my_alias} ->> {child_alias}: {child.name}")
                lines.extend(render_span(child))
                lines.append(f"    {child_alias} -->> {my_alias}")

        if span.duration_ms is not None:
            lines.append(f"    Note over {my_alias}: {span.duration_ms:.0f}ms")

        lines.append(f"    deactivate {my_alias}")
        return lines

    # Render roots sequentially
    for i, root in enumerate(roots):
        if i > 0:
            parts.append("    rect rgb(191, 191, 191)")
        parts.extend(render_span(root))
        if i > 0:
            parts.append("    end")

    return "\n".join(parts)