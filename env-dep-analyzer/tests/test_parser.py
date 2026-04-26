import pytest
from env_dependency_analyzer.parser import extract_refs, parse_dotenv, parse_compose, scan_directory
from pathlib import Path
import networkx as nx


def test_extract_refs():
    assert extract_refs("postgres://${DB_HOST:-localhost}:${DB_PORT}/db") == {"DB_HOST", "DB_PORT"}
    assert extract_refs("$NODE_ENV") == {"NODE_ENV"}
    assert extract_refs('DEBUG="${LOG_LEVEL:-info}"') == {"LOG_LEVEL"}
    assert extract_refs("no$var") == set()
    assert extract_refs("${VAR}") == {"VAR"}


def test_parse_dotenv(sample_env):
    defined, edges = parse_dotenv(sample_env, set())
    assert defined == {"DB_HOST", "DB_PORT", "DB_URL", "API_KEY"}
    assert len(edges) == 3  # DB_URL->DB_HOST, DB_URL->DB_PORT, API_KEY->SECRET_KEY
    assert any(e == ("DB_URL", "DB_HOST") for e in edges)


def test_parse_compose(sample_compose, sample_env, tmp_path):
    defined, edges = parse_compose(sample_compose, set())
    assert "DB_URL" in defined
    assert any(e == ("DB_URL", "DB_HOST") for e in edges)
    assert len(defined) >= 2


def test_scan_directory(tmp_path, sample_env, sample_compose):
    defined, edges, files = scan_directory(tmp_path)
    assert len(files) >= 2
    G = nx.DiGraph(edges)
    assert G.has_edge("DB_URL", "DB_HOST")
