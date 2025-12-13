import pytest
from dockerfile_optimizer.suggester import suggest_optimized
from dockerfile_optimizer.parser import Instruction


def test_combine_runs():
    insts = [
        Instruction("FROM", "ubuntu", 1, ""),
        Instruction("RUN", "apt update", 2, ""),
        Instruction("RUN", "apt install curl", 3, ""),
        Instruction("COPY", ". /app", 4, ""),
    ]
    optimized = suggest_optimized(insts)
    assert "RUN apt update && \\" in optimized
    assert "apt install curl" in optimized
    assert "COPY . /app" in optimized


def test_no_runs():
    insts = [Instruction("FROM", "alpine", 1, ""), Instruction("COPY", ".", 2, "")]
    optimized = suggest_optimized(insts)
    assert len(optimized.splitlines()) == 2
