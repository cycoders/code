import jwt
from datetime import timedelta, datetime
from oauth_flow_tester.tokens import generate_access_token, inspect_token, SECRET_KEY
from rich.console import Console


def test_generate_access_token():
    token = generate_access_token("test-client", "read")
    payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
    assert payload["sub"] == "test-client"
    assert payload["scope"] == "read"
    assert isinstance(payload["exp"], int)
    assert payload["exp"] > payload["iat"]


def test_inspect_token_valid(capfd):
    token = generate_access_token("test")
    console = Console(file=capfd.readouterr())
    inspect_token(token, console)
    captured = capfd.readouterr()
    assert "✅ Signature valid" in captured.out


def test_inspect_token_invalid(capfd):
    invalid_token = "eyJhbGciOiJIUzI1NiJ9.invalid"
    console = Console(file=capfd.readouterr())
    inspect_token(invalid_token, console)
    captured = capfd.readouterr()
    assert "❌ Invalid token" in captured.out
