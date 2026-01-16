from shell_recorder_cli.exporter import export_md


def test_export_md(sample_session, tmp_path):
    out = tmp_path / "test.md"
    export_md(sample_session, out, title="Test Session")

    assert out.exists()
    content = out.read_text()
    assert "# Test Session" in content
    assert "```bash" in content
    assert "REC> ls" in content
    assert "Duration: 1.5s" in content
