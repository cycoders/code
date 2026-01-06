import pytest
from click.testing import Result
from pathlib import Path
from smtp_catcher.storage import init_db, save_email
from smtp_catcher.cli import app
from smtp_catcher.email_parser import parse_email_parts


class TestCLI:
    def test_list_empty(self, runner: pytest.fixture, tmp_data_dir: Path) -> None:
        result: Result = runner.invoke(app, ["emails", "list", "--data-dir", str(tmp_data_dir)])
        assert result.exit_code == 0
        assert "No emails found" in result.stdout

    def test_list_after_save(self, runner: pytest.fixture, tmp_data_dir: Path) -> None:
        # Save test email
        email_dict = {
            "sender": "test@example.com",
            "recipients": ["bob@example.com"],
            "subject": "Test",
            "body_text": "Hello",
            "body_html": None,
            "headers": {"X-Test": "1"},
        }
        save_email(tmp_data_dir, email_dict)

        result: Result = runner.invoke(app, ["emails", "list", "--data-dir", str(tmp_data_dir)])
        assert result.exit_code == 0
        assert "test@example.com" in result.stdout
        assert "Test" in result.stdout

    def test_show(self, runner: pytest.fixture, tmp_data_dir: Path) -> None:
        save_email(tmp_data_dir, {
            "sender": "alice@test.com",
            "recipients": ["bob@test.com"],
            "subject": "Hi",
            "body_text": "World",
            "headers": {"Foo": "bar"},
        })
        # Get ID (last insert 1)
        from smtp_catcher.storage import get_email
        email = get_email(tmp_data_dir, 1)
        assert email

        result = runner.invoke(app, ["emails", "show", "1", "--data-dir", str(tmp_data_dir)])
        assert result.exit_code == 0
        assert "alice@test.com" in result.stdout
        assert "World" in result.stdout

    def test_show_missing(self, runner: pytest.fixture, tmp_data_dir: Path) -> None:
        result = runner.invoke(app, ["emails", "show", "999", "--data-dir", str(tmp_data_dir)])
        assert result.exit_code == 1
        assert "not found" in result.stdout

    def test_filter_sender(self, runner: pytest.fixture, tmp_data_dir: Path) -> None:
        save_email(tmp_data_dir, {"sender": "foo@ex.com", "recipients": [], "subject": "", "body_text": "", "headers": {}})
        save_email(tmp_data_dir, {"sender": "bar@ex.com", "recipients": [], "subject": "", "body_text": "", "headers": {}})
        result = runner.invoke(app, ["emails", "list", "--sender", "foo", "--data-dir", str(tmp_data_dir)])
        assert result.exit_code == 0
        assert "foo@ex.com" in result.stdout
        assert "bar@ex.com" not in result.stdout