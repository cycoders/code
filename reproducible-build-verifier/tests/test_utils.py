from pathlib import Path
from reproducible_build_verifier.utils import file_hash

def test_hash_stability(tmp_path):
    f = tmp_path / 't.txt'
    f.write_text('hello')
    assert file_hash(f) == file_hash(f)