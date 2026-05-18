import tempfile, os
from gc_log_analyzer.cli import main

def test_cli_runs(capsys, monkeypatch):
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".log") as f:
        f.write("[0.1s] GC Pause Young 5ms\n")
        fname = f.name
    try:
        monkeypatch.setattr("sys.argv", ["prog", fname])
        main()
        out = capsys.readouterr().out
        assert "Pauses" in out
    finally:
        os.unlink(fname)