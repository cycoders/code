import json
import pytest
from pathlib import Path
from datetime import datetime
from smtp_catcher.storage import (
    init_db,
    save_email,
    list_email_summaries,
    get_email,
    delete_email,
    clear_emails,
)


class TestStorage:
    @pytest.fixture(autouse=True)
    def setup(self, tmp_data_dir: Path):
        init_db(tmp_data_dir)
        self.data_dir = tmp_data_dir

    def test_save_and_list(self, tmp_data_dir: Path):
        email = {
            "sender": "test@example.com",
            "recipients": ["to@example.com"],
            "subject": "Test Subject",
            "body_text": "Hello",
            "body_html": "<p>Hello</p>",
            "headers": {"User-Agent": "test"},
        }
        save_email(tmp_data_dir, email)

        summaries = list_email_summaries(tmp_data_dir, limit=5)
        assert len(summaries) == 1
        s = summaries[0]
        assert s["sender"] == "test@example.com"
        assert s["recipients_count"] == 1
        assert s["subject"] == "Test Subject"

    def test_get_email(self, tmp_data_dir: Path):
        save_email(tmp_data_dir, {"sender": "a@b.com", "recipients": [], "subject": "", "body_text": "", "headers": {"h": "v"}})
        email = get_email(tmp_data_dir, 1)
        assert email is not None
        assert email["sender"] == "a@b.com"
        assert email["recipients"] == []
        assert email["headers"] == {"h": "v"}

    def test_delete(self, tmp_data_dir: Path):
        save_email(tmp_data_dir, {"sender": "del@test.com", "recipients": [], "subject": "", "body_text": "", "headers": {}})
        assert delete_email(tmp_data_dir, 1)
        assert get_email(tmp_data_dir, 1) is None

    def test_clear(self, tmp_data_dir: Path):
        for i in range(3):
            save_email(tmp_data_dir, {"sender": f"c{i}@test.com", "recipients": [], "subject": "", "body_text": "", "headers": {}})
        clear_emails(tmp_data_dir)
        assert list_email_summaries(tmp_data_dir) == []

    def test_filter(self, tmp_data_dir: Path):
        save_email(tmp_data_dir, {"sender": "foo@bar.com", "recipients": [], "subject": "", "body_text": "", "headers": {}})
        save_email(tmp_data_dir, {"sender": "baz@bar.com", "recipients": [], "subject": "", "body_text": "", "headers": {}})
        filtered = list_email_summaries(tmp_data_dir, sender_filter="foo")
        assert len(filtered) == 1
        assert "foo" in filtered[0]["sender"]