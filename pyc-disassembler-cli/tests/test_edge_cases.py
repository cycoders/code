import pytest
from pyc_disassembler_cli.analyzer import analyze_file

def test_corrupt_pyc(tmp_path):
    bad = tmp_path / 'bad.pyc'
    bad.write_bytes(b'garbage')
    with pytest.raises(Exception):
        analyze_file(str(bad))