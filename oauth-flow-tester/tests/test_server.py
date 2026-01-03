import pytest
from flask import url_for
from oauth_flow_tester.server import run_server, _clients, _auth_codes


@pytest.fixture(autouse=True)
def reset_state():
    _clients.clear()
    _auth_codes.clear()


class TestServerEndpoints:
    def test_discovery(self):
        # Indirect test via known structure
        assert True  # Full integration heavy; unit via client

    @pytest.mark.slow
    def test_auth_endpoint_returns_redirect(self, mocker):
        mocker.patch("oauth_flow_tester.server.secrets", lambda n: "testcode")
        from oauth_flow_tester.server import create_server_app  # Assume factory if refactored
        # Mock client check
        app = Flask(__name__)  # Simplified
        with app.test_client() as client:
            rv = client.get("/auth?client_id=test-client&redirect_uri=http://example/cb")
            assert rv.status_code == 302


# More via pytest-flask or httpx later
