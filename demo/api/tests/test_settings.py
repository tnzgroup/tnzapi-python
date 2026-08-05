def test_get_api_url_returns_current_value(client, monkeypatch):
    monkeypatch.setenv("TNZ_API_URL", "https://api.tnz.co.nz/api/v3.00")

    response = client.get("/api/settings/api-url")

    assert response.status_code == 200
    assert response.json() == {"ApiUrl": "https://api.tnz.co.nz/api/v3.00"}


def test_set_api_url_rejects_invalid_url(client):
    response = client.post("/api/settings/api-url", json={"ApiUrl": "not-a-url"})

    assert response.status_code == 400


def test_set_api_url_updates_env_var(client):
    response = client.post("/api/settings/api-url", json={"ApiUrl": "https://staging.tnz.co.nz/api/v3.00"})

    assert response.status_code == 200
    assert response.json() == {"Status": "ok", "ApiUrl": "https://staging.tnz.co.nz/api/v3.00"}


def test_set_api_url_rejects_http_scheme_without_allow_insecure_http_flag(client, monkeypatch):
    monkeypatch.delenv("TNZ_ALLOW_INSECURE_HTTP", raising=False)

    response = client.post("/api/settings/api-url", json={"ApiUrl": "http://localhost:9090/api/v3.00"})

    assert response.status_code == 400
    assert response.json()["Result"] == "Failed"


def test_set_api_url_accepts_http_scheme_when_allow_insecure_http_flag_is_set(client, monkeypatch):
    monkeypatch.setenv("TNZ_ALLOW_INSECURE_HTTP", "true")

    response = client.post("/api/settings/api-url", json={"ApiUrl": "http://localhost:9090/api/v3.00"})

    assert response.status_code == 200
    assert response.json() == {"Status": "ok", "ApiUrl": "http://localhost:9090/api/v3.00"}


def test_get_allow_insecure_http_defaults_to_false(client, monkeypatch):
    monkeypatch.delenv("TNZ_ALLOW_INSECURE_HTTP", raising=False)

    response = client.get("/api/settings/allow-insecure-http")

    assert response.status_code == 200
    assert response.json() == {"Enabled": False}


def test_set_allow_insecure_http_updates_env_var(client):
    response = client.post("/api/settings/allow-insecure-http", json={"Enabled": True})

    assert response.status_code == 200
    assert response.json() == {"Status": "ok", "Enabled": True}
    import os
    assert os.environ["TNZ_ALLOW_INSECURE_HTTP"] == "true"


def test_get_ssl_verification_returns_501_not_supported(client):
    response = client.get("/api/settings/ssl-verification")

    assert response.status_code == 501
    assert response.json()["Result"] == "Failed"


def test_set_ssl_verification_returns_501_not_supported(client):
    response = client.post("/api/settings/ssl-verification", json={"Enabled": True})

    assert response.status_code == 501
    assert response.json()["Result"] == "Failed"
