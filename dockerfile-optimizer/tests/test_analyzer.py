import pytest
from dockerfile_optimizer.analyzer import analyze
from dockerfile_optimizer.parser import Instruction


@pytest.fixture
def multi_run_insts():
    return [
        Instruction("FROM", "node:18", 1, ""),
        Instruction("RUN", "npm ci", 2, ""),
        Instruction("RUN", "npm run build", 3, ""),
        Instruction("COPY", ". /app", 4, ""),
    ]


def test_multiple_runs(multi_run_insts):
    analysis = analyze(multi_run_insts)
    assert len(analysis["issues"]) >= 1
    assert "Multiple RUNs (2)" in analysis["issues"][0]
    assert analysis["potential_savings_mb"] > 0


def test_cache_bust():
    insts = [
        Instruction("FROM", "ubuntu", 1, ""),
        Instruction("RUN", "apt-get install gcc", 2, ""),
        Instruction("COPY", ". /src", 3, ""),
    ]
    analysis = analyze(insts)
    assert any("Cache bust" in i for i in analysis["issues"])


def test_no_issues():
    insts = [Instruction("FROM", "alpine", 1, ""), Instruction("COPY", ".", 2, "")]
    analysis = analyze(insts)
    assert not analysis["issues"]
