from cors_auditor_cli.models import AuditConfig


def test_config_url_validation():
    config = AuditConfig(url="https://example.com", origins=["http://loc:3000"], methods=["GET"])
    assert config.url == "https://example.com"


def test_invalid_url():
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        AuditConfig(url="example.com", origins=["http://loc:3000"], methods=["GET"])