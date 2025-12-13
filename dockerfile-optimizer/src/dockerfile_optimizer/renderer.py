from typing import List, Optional

from .parser import Instruction


@Optional(str)
def render_mermaid(
    instructions: List[Instruction], output_file: Optional[str] = None
) -> str:
    """
    Render layer dependency graph as Mermaid flowchart.
    """
    mermaid = "```mermaid\ngraph TD\n"
    for idx, inst in enumerate(instructions):
        label = f'{inst.command} {inst.args[:35]}...'
        node = f"N{idx}"
        mermaid += f"    {node}[\"{label}\"]\n"
        if idx > 0:
            mermaid += f"    N{idx-1} --> {node}\n"
    mermaid += "```\n"
    if output_file:
        with open(output_file, "w") as f:
            f.write(mermaid)
    return mermaid
