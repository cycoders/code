from typer.testing import CliRunner
import json

from jwt_cli.cli import app

runner = CliRunner()

# Decode
def test_decode_hs(hs_token):
    result = runner.invoke(app, ["decode", hs_token])
    assert result.exit_code == 0
    assert "HS256" in result.stdout

# JSON out
def test_decode_json(hs_token):
    result = runner.invoke(app, ["decode", hs_token, "--json"])
    assert result.exit_code == 0
    data = json.loads(result.stdout)
    assert data["header"]["alg"] == "HS256"

# Sign
def test_sign_cli(hs_secret):
    payload = '{"sub":"cli","exp":9999999999}'
    result = runner.invoke(app, ["sign", "--key", "secret", "--alg", "HS256"], input=payload)
    assert result.exit_code == 0
    token = result.stdout.strip()
    decoded = jwt.decode(token, "secret", algorithms=["HS256"])
    assert decoded["sub"] == "cli"

# Validate
def test_validate_valid(hs_token, hs_secret):
    result = runner.invoke(app, ["validate", hs_token, "--key", hs_secret.decode()])
    assert result.exit_code == 0
    assert "VALID" in result.stdout

# Invalid
def test_validate_invalid_key(hs_token, rsa_public_pem):
    result = runner.invoke(app, ["validate", hs_token, "--key-file", io.BytesIO(rsa_public_pem)])
    assert result.exit_code == 1
    assert "INVALID" in result.stdout
    assert "signature" in result.stdout