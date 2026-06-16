from rbac_visualizer.render import render_mermaid

def test_mermaid_output():
    g = {'subject:dev': ['role:edit']}
    out = render_mermaid(g)
    assert 'dev --> edit' in out