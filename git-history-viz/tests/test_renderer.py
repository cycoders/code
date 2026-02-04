from git_history_viz.renderer import render_mermaid, render_html, escape_mermaid
from git_history_viz.parser import parse_repo


class TestRenderer:
    def test_mermaid_contains_elements(self, sample_repo):
        commits = parse_repo(str(sample_repo), None, 10)
        from git_history_viz.graph import topological_sort
        order = topological_sort(commits)
        diagram = render_mermaid(commits, order, "default")
        assert "flowchart TD" in diagram
        assert "-->" in diagram
        assert "classDef" in diagram

    def test_escape_mermaid(self):
        assert escape_mermaid('He said "hi"') == "He said \"hi\""
        assert escape_mermaid("\\back") == "\\\\back"

    def test_html_renders(self, sample_repo):
        commits = parse_repo(str(sample_repo), None, 10)
        from git_history_viz.graph import topological_sort
        diagram = render_mermaid(commits, [], "dark")
        html = render_html(diagram, "dark")
        assert "<html>" in html
        assert "mermaid.initialize" in html
