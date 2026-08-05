import pytest

from tnzapi.core.auth import TNZApiUser


def test_defaults_to_v300_base_url():
    user = TNZApiUser(auth_token="abc123")
    assert user.AuthToken == "abc123"
    assert user.BaseURL == "https://api.tnz.co.nz/api/v3.00"


def test_base_url_overridable():
    user = TNZApiUser(auth_token="abc123", base_url="https://staging.tnz.co.nz/api/v3.00")
    assert user.BaseURL == "https://staging.tnz.co.nz/api/v3.00"


def test_auth_token_required():
    with pytest.raises(ValueError):
        TNZApiUser(auth_token="")


def test_base_url_falls_back_to_env_var(monkeypatch):
    monkeypatch.setenv("TNZ_API_URL", "https://env.tnz.co.nz/api/v3.00")
    user = TNZApiUser(auth_token="abc123")

    assert user.BaseURL == "https://env.tnz.co.nz/api/v3.00"


def test_explicit_base_url_overrides_env_var(monkeypatch):
    monkeypatch.setenv("TNZ_API_URL", "https://env.tnz.co.nz/api/v3.00")
    user = TNZApiUser(auth_token="abc123", base_url="https://explicit.tnz.co.nz/api/v3.00")

    assert user.BaseURL == "https://explicit.tnz.co.nz/api/v3.00"


def test_auth_token_falls_back_to_env_var(monkeypatch):
    monkeypatch.setenv("TNZ_AUTH_TOKEN", "env-token-123")
    user = TNZApiUser()

    assert user.AuthToken == "env-token-123"


def test_explicit_auth_token_overrides_env_var(monkeypatch):
    monkeypatch.setenv("TNZ_AUTH_TOKEN", "env-token-123")
    user = TNZApiUser(auth_token="explicit-token")

    assert user.AuthToken == "explicit-token"


def test_auth_token_required_still_raises_without_env_var(monkeypatch):
    monkeypatch.delenv("TNZ_AUTH_TOKEN", raising=False)
    with pytest.raises(ValueError):
        TNZApiUser()


def test_new_pascalcase_kwargs_work():
    user = TNZApiUser(AuthToken="tok123", BaseURL="https://example.com")
    assert user.AuthToken == "tok123"
    assert user.BaseURL == "https://example.com"


def test_old_snake_case_kwargs_still_work_with_warning():
    with pytest.warns(DeprecationWarning):
        user = TNZApiUser(auth_token="tok123", base_url="https://example.com")
    assert user.AuthToken == "tok123"
    assert user.BaseURL == "https://example.com"
