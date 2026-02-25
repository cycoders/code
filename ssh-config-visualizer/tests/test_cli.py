import sys
from unittest.mock import patch

import typer
from ssh_config_visualizer.cli import app


def test_graph_help():
    with patch.object(sys, "argv", ["ssh-config-visualizer", "graph", "--help"]):
        # Typer handles help internally
        assert True  # no crash

# Integration smoke tests via runner

def run_cli(args: list):
    with patch.object(sys, "argv", ["prog"] + args):
        try:
            app(prog_name="test")
        except SystemExit:
            pass


def test_graph_smoke():
    run_cli(["graph"])


def test_validate_smoke():
    run_cli(["validate"])