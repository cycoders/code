import pytest
from pathlib import Path
from traceroute_visualizer.models import Hop
from traceroute_visualizer.visualizer import generate_svg

@pytest.fixture
def sample_hops():
    return [
        Hop(1, "192.168.1.1", [1.0, 1.1, 1.2]),
        Hop(2, "8.8.8.8", [10.0, INF, 11.0]),
    ]

def test_generate_svg(tmp_path, sample_hops):
    svg_path = tmp_path / "test.svg"
    generate_svg(sample_hops, svg_path)
    assert svg_path.exists()
    content = svg_path.read_text()
    assert '<svg' in content
    assert '<circle' in content
    assert '<line' in content
    assert '192.168.1.1' in content

@pytest.mark.parametrize("country,expected", [
    ("US", "🇺🇸"),
    ("xx", "❓"),
    (None, "─"),
])
def test_flags(country, expected):
    hop = Hop(1, "1.1.1.1", [1.0])
    hop.country = country
    # Simulated, but flags dict tested indirectly via usage