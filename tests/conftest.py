from dotenv import load_dotenv

load_dotenv()
load_dotenv(".env.local", override=True)
load_dotenv(".env.test", override=True)

import pytest
import responses as responses_lib
from tnzapi.core.auth import TNZApiUser

API_BASE_URL = "https://api.tnz.co.nz/api/v3.00"


@pytest.fixture(autouse=True)
def _isolate_from_local_env(monkeypatch):
    # A developer's real .env/.env.local (e.g. TNZ_API_URL pointing at a local
    # test server) must never leak into a test that doesn't explicitly opt in
    # via its own monkeypatch.setenv(...) - keeps the whole suite hermetic
    # regardless of local dev environment configuration.
    monkeypatch.delenv("TNZ_API_URL", raising=False)
    monkeypatch.delenv("TNZ_AUTH_TOKEN", raising=False)
    monkeypatch.delenv("TNZ_ALLOW_INSECURE_HTTP", raising=False)


@pytest.fixture
def api_user():
    # Explicit BaseURL keeps unit tests isolated from any local .env/.env.local
    # TNZ_API_URL override (e.g. pointing at a local test server) - unit tests
    # mock https://api.tnz.co.nz directly and must not depend on ambient env config.
    return TNZApiUser(AuthToken="test-auth-token-123", BaseURL=API_BASE_URL)


def mock_endpoint(method: str, path: str, **kwargs):
    # Thin wrapper over responses_lib.add() that prepends the shared API_BASE_URL,
    # so a base-URL change (or API version bump) only needs updating in one place
    # instead of at every one of this suite's mocked-endpoint call sites.
    return responses_lib.add(method, f"{API_BASE_URL}{path}", **kwargs)
