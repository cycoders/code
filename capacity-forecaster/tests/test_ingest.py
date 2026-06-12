import tempfile, os, pandas as pd
from capacity_forecaster.ingest import load_series

def test_load_series():
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write('date,value\n2024-01-01,100\n2024-01-02,110')
        path = f.name
    try:
        vals = load_series(path)
        assert len(vals) == 2
    finally:
        os.unlink(path)