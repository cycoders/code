import pytest
from pathlib import Path

from env_usage_scanner.output import generate_template, generate_mermaid_graph, print_scan_results  # Direct import for test

from env_usage_scanner.models import Usage
from env_usage_scanner.scanner import scan_directory


@pytest.mark.parametrize("vars_dict,expected",
    [({ "DB_URL": [] }, "# Auto-generated .env template by env-usage-scanner\nDB_URL=" ), ] )
def test_generate_template(vars_dict, expected, temp_dir: Path):
    assert generate_template(vars_dict) == expected

    out = temp_dir / "template.env"
    generate_template(vars_dict, out)
    assert out.read_text().strip() == expected.strip()


def test_generate_mermaid(temp_dir: Path):
    usages = {
        "DB": [Usage(temp_dir / "app.py", 1, "DB", "snippet", "py")]
    }
    graph = generate_mermaid_graph(usages)
    assert "app.py --> \"DB\"" in graph


def test_scan_print(temp_dir: Path, capsys):
    (temp_dir / "test.py").write_text("os.getenv('VAR')")
    usages = scan_directory(temp_dir)
    print_scan_results(usages)
    captured = capsys.readouterr()
    assert "VAR" in captured.out
