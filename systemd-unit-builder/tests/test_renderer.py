from systemd_unit_builder.renderer import render_unit

def test_render_basic():
    data = {"Unit": {"Description": "demo"}, "Service": {"ExecStart": "/bin/true"}}
    out = render_unit(data)
    assert "[Unit]" in out and "Description=demo" in out