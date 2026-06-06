import tempfile, yaml
from bloom_filter_cli.simulator import run

def test_simulator_runs():
    cfg = {"elements": 1000, "m": 8192, "k": 5}
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump(cfg, f)
        f.flush()
        result = run(f.name)
        assert "estimated_fp" in result