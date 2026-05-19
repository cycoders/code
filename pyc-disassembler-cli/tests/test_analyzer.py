import pytest
from pyc_disassembler_cli.analyzer import analyze_file

def test_analyze_valid_pyc(tmp_path):
    pyc = tmp_path / 'test.pyc'
    # minimal valid header + marshal for empty code object
    pyc.write_bytes(b'\x6f\x0d\x0d\x0a' + b'\x00'*12 + b'\x00')
    assert 'CFG' in analyze_file(str(pyc))