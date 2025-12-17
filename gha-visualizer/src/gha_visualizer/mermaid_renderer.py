from typing import List

from .models import Job


def generate_mermaid(jobs: List[Job]) -> str:
    """Generate Mermaid flowchart from list of Jobs."""

    lines = [
        "flowchart TD",
        "    classDef job fill:#e1f5fe,stroke:#01579b,stroke-width:3px,color:#000",
        "    classDef step fill:#f3e5f5,stroke:#4a148c,stroke-width:2px"
    ]

    job_ids: dict[str, str] = {}
    for job in jobs:
        safe_id = job.name.replace('-', '_').replace('.', '_').replace('/', '_')
        job_ids[job.name] = safe_id

        label = job.name
        if job.strategy:
            label += " [matrix]"
        lines.append(f"    {safe_id}[\"{label}\"]")
        lines.append(f"    {safe_id}:::job")

    # Dependencies
    for job in jobs:
        safe_id = job_ids[job.name]
        for need in job.needs:
            if need in job_ids:
                need_id = job_ids[need]
                lines.append(f"    {need_id} --> {safe_id}")

    # Steps subgraphs (limit to 6 for readability)
    for job in jobs:
        safe_id = job_ids[job.name]
        if job.steps:
            lines.append(f"    subgraph {safe_id}_steps [\"{job.name} Steps\"]")
            lines.append("        direction TB")
            for i, step in enumerate(job.steps[:6]):
                step_desc = (
                    (step.get('run') or step.get('uses', '???')).split('\n')[0]
                )
                if len(step_desc) > 30:
                    step_desc = step_desc[:27] + "..."
                step_id = f"{safe_id}_s{i}"
                lines.append(f"        {step_id}[\"{step_desc}\"]")
                lines.append(f"        {step_id}:::step")
                lines.append(f"        {safe_id} -.-> {step_id}")
            if len(job.steps) > 6:
                lines.append(f"        ... +{len(job.steps)-6} more")
            lines.append("    end")

    return '\n'.join(lines)