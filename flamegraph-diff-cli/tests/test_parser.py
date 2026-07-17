from flamegraph_diff_cli.parser import parse_folded
import tempfile, os

def test_parse_basic():
    with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
        f.write('main;foo 10\nmain;bar 5\n')
        name = f.name
    try:
        assert parse_folded(name) == {'main;foo': 10, 'main;bar': 5}
    finally:
        os.unlink(name)