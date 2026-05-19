from pyc_disassembler_cli.graph import ControlFlowGraph

def test_cfg_creation():
    cfg = ControlFlowGraph()
    assert len(cfg.blocks) == 0