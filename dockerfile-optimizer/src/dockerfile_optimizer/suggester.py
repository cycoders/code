from typing import List

from .parser import Instruction


def suggest_optimized(instructions: List[Instruction]) -> str:
    """
    Suggest an optimized Dockerfile by combining consecutive RUNs.

    Advanced: reorder deps before COPY (future).
    """
    optimized_lines = []
    i = 0
    n = len(instructions)
    while i < n:
        inst = instructions[i]
        if inst.command == "RUN":
            run_cmds = [inst.args]
            i += 1
            # Greedily combine consecutive RUNs
            while i < n and instructions[i].command == "RUN":
                run_cmds.append(instructions[i].args)
                i += 1
            # Format multiline
            combined = " && \\\n    ".join(run_cmds)
            optimized_lines.append(f"RUN {combined}")
        else:
            optimized_lines.append(f"{inst.command} {inst.args}")
            i += 1
    return "\n".join(optimized_lines)
