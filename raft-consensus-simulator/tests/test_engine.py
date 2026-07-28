import pytest
from raft_consensus_simulator.engine import RaftEngine
from raft_consensus_simulator.models import LogEntry

def test_initial_state():
    engine = RaftEngine(3)
    assert len(engine.nodes) == 3

def test_step_advances_time():
    engine = RaftEngine(3)
    engine.step()
    assert engine.time == 1

def test_apply_log():
    engine = RaftEngine(3)
    engine.apply_log(0, LogEntry(term=1, command="set x=1"))
    assert engine.nodes[0].commit_index == 0