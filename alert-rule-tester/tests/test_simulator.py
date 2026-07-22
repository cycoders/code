import pytest
from alert_rule_tester.simulator import simulate

def test_empty_rules(tmp_path):
    (tmp_path / "empty.yaml").write_text("{}")
    result = simulate(str(tmp_path), "samples.jsonl", "1h")
    assert result == []

def test_basic_rule(tmp_path):
    rule = tmp_path / "cpu.yaml"
    rule.write_text("alert: HighCPU\nexpr: cpu > 80")
    result = simulate(str(tmp_path), "samples.jsonl", "1h")
    assert len(result) == 1

def test_invalid_yaml(tmp_path):
    (tmp_path / "bad.yaml").write_text(":::")
    with pytest.raises(Exception):
        simulate(str(tmp_path), "samples.jsonl", "1h")