from click.testing import CliRunner
from systemd_unit_builder.cli import main

def test_cli_runs(tmp_path):
    cfg = tmp_path / "s.yaml"
    cfg.write_text("name: demo\nexec_start: /bin/true")
    runner = CliRunner()
    result = runner.invoke(main, ["--config", str(cfg), "--out", "-"])
    assert result.exit_code == 0
    assert "[Service]" in result.output