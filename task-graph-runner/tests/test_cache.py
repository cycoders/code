from task_graph_runner.cache import ContentCache
from pathlib import Path
import tempfile

def test_cache_key_stable():
    with tempfile.TemporaryDirectory() as tmp:
        c = ContentCache(Path(tmp))
        k1 = c.key('t', {'a': 1})
        k2 = c.key('t', {'a': 1})
        assert k1 == k2