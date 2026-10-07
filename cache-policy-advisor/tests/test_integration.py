import tempfile
from pathlib import Path

def test_end_to_end():
    with tempfile.TemporaryDirectory() as tmp:
        log = Path(tmp) / 'access.log'
        log.write_text('127.0.0.1 - - [10/Oct/2020:13:55:36 +0000] "GET / HTTP/1.1" 304 0\n')
        assert 'hit_rate' in str(log)