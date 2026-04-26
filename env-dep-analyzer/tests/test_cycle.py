import pytest
from env_dependency_analyzer.parser import parse_dotenv, scan_directory
from pathlib import Path
import networkx as nx


def test_cycle_detection(tmp_path):
    cycle_env = tmp_path / ".env"
    cycle_env.write_text("A=${B}\nB=${A}\n")
    defined, edges = parse_dotenv(cycle_env, set())
    G = nx.DiGraph(edges)
    cycles = list(nx.simple_cycles(G))
    assert len(cycles) == 1
    assert set(cycles[0]) == {"A", "B"}


def test_no_cycle(tmp_path):
    no_cycle = tmp_path / ".env"
    no_cycle.write_text("A=${B}\nB=prod\n")
    defined, edges = parse_dotenv(no_cycle, set())
    G = nx.DiGraph(edges)
    cycles = list(nx.simple_cycles(G))
    assert len(cycles) == 0
