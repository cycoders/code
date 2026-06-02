import yaml
from systemd_unit_builder.validator import validate_config
from systemd_unit_builder.hardener import apply_hardening
from systemd_unit_builder.renderer import render_unit

def test_full_pipeline():
    raw = {"name": "api", "exec_start": "/opt/api", "after": ["network.target"]}
    cfg = validate_config(raw)
    hardened = apply_hardening(cfg)
    unit = render_unit(hardened)
    assert "After=network.target" in unit