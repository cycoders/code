from pyc_disassembler_cli.hints import suggest_optimizations

def test_hint_generation():
    assert len(suggest_optimizations([])) == 0