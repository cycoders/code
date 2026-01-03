from flask import Flask, request, redirect, jsonify, abort
from urllib.parse import urlencode
from threading import RLock
from .utils import generate_pkce_pair
from .tokens import generate_access_token, SECRET_KEY
from .types import TokenResponse

# Thread-safe storage
_clients_lock = RLock()
_auth_codes_lock = RLock()

_clients = {
    "test-client": {
        "secret": "test-secret",
        "redirect_uris": ["http://127.0.0.1:9090/callback"],
    }
}
_auth_codes = {}


def run_server(host: str = "127.0.0.1", port: int = 8080) -> None:
    """Run the Flask OAuth mock server."""
    app = Flask(__name__)

    @app.route("/.well-known/openid-configuration")
    def discovery():
        return jsonify({
            "issuer": f"https://{host}:{port}",
            "authorization_endpoint": f"http://{host}:{port}/auth",
            "token_endpoint": f"http://{host}:{port}/token",
            "jwks_uri": f"http://{host}:{port}/.well-known/jwks.json",
            "scopes_supported": ["read", "write"],
            "grant_types_supported": ["authorization_code", "client_credentials"],
        })

    @app.route("/.well-known/jwks.json")
    def jwks():
        return jsonify({
            "keys": [
                {
                    "kty": "oct",
                    "kid": "HS256-test",
                    "use": "sig",
                    "k": SECRET_KEY,
                }
            ],
        })

    @app.route("/auth")
    def authorize():
        client_id = request.args.get("client_id")
        redirect_uri = request.args.get("redirect_uri")
        scope = request.args.get("scope", "")
        state = request.args.get("state", "")
        code_challenge = request.args.get("code_challenge")
        code_challenge_method = request.args.get("code_challenge_method", "plain")

        with _clients_lock:
            if client_id not in _clients:
                abort(400, "Invalid client_id")
            client = _clients[client_id]
            if redirect_uri not in client["redirect_uris"]:
                abort(400, "Invalid redirect_uri")

        code = secrets.token_urlsafe(32)
        with _auth_codes_lock:
            _auth_codes[code] = {
                "client_id": client_id,
                "redirect_uri": redirect_uri,
                "scope": scope,
                "state": state,
                "code_challenge": code_challenge,
                "code_challenge_method": code_challenge_method,
            }

        params = {"code": code, "state": state}
        uri = f"{redirect_uri}?{urlencode(params)}"
        return redirect(uri, code=302)

    @app.route("/token", methods=["POST"])
    def issue_token():
        grant_type = request.form.get("grant_type")
        client_id = request.form.get("client_id")

        if grant_type == "authorization_code":
            code = request.form.get("code")
            redirect_uri = request.form.get("redirect_uri")
            code_verifier = request.form.get("code_verifier")

            with _auth_codes_lock:
                if code not in _auth_codes:
                    abort(400, "invalid_grant")
                stored = _auth_codes.pop(code)

            if stored["client_id"] != client_id or stored["redirect_uri"] != redirect_uri:
                abort(400, "invalid_grant")

            if stored["code_challenge"]:
                if stored["code_challenge_method"] == "S256":
                    verifier_challenge = hashlib.sha256(code_verifier.encode()).digest()
                    verifier_challenge = base64.urlsafe_b64encode(verifier_challenge).decode().rstrip("=")
                else:
                    verifier_challenge = code_verifier
                if verifier_challenge != stored["code_challenge"]:
                    abort(400, "invalid_grant")

            token = generate_access_token(client_id, stored["scope"])
            return TokenResponse(
                access_token=token,
                expires_in=3600,
                scope=stored["scope"],
            ).model_dump()

        elif grant_type == "client_credentials":
            client_secret = request.form.get("client_secret")
            with _clients_lock:
                if client_id not in _clients or _clients[client_id]["secret"] != client_secret:
                    abort(401, "invalid_client")
            token = generate_access_token(client_id)
            return TokenResponse(access_token=token, expires_in=3600).model_dump()

        abort(400, "unsupported_grant_type")

    app.run(host=host, port=port, debug=False, use_reloader=False)
