from dataclasses import dataclass

@dataclass
class BasicBlock:
    start: int
    end: int
    opcodes: list

class ControlFlowGraph:
    def __init__(self):
        self.blocks = []
    def to_format(self, fmt):
        return f"CFG with {len(self.blocks)} blocks ({fmt})"