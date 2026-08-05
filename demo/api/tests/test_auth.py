def test_set_token_rejects_empty_token(client):
    response = client.post("/api/auth/token", json={"Token": ""})

    assert response.status_code == 400
    assert response.json()["Result"] == "Failed"


def test_set_token_rejects_non_jwt_shaped_token(client):
    response = client.post("/api/auth/token", json={"Token": "not-a-jwt"})

    assert response.status_code == 400
    assert response.json()["Result"] == "Failed"


def test_set_token_accepts_jwt_shaped_token(client):
    response = client.post("/api/auth/token", json={"Token": "aaa.bbb.ccc"})

    assert response.status_code == 200
    assert response.json() == {"Status": "ok"}


def test_set_token_never_places_the_real_token_in_the_cookie(client):
    response = client.post("/api/auth/token", json={"Token": "secret-header.secret-payload.secret-sig"})

    set_cookie = response.headers["set-cookie"]
    assert "secret-header.secret-payload.secret-sig" not in set_cookie
    assert "demo_session_id=" in set_cookie
    assert "httponly" in set_cookie.lower()


def test_second_request_with_the_session_cookie_resolves_the_overridden_token(client):
    from app.routers.auth import resolve_auth_token

    first = client.post("/api/auth/token", json={"Token": "aaa.bbb.ccc"})
    session_id = first.cookies["demo_session_id"]

    class _FakeRequest:
        cookies = {"demo_session_id": session_id}

    assert resolve_auth_token(_FakeRequest()) == "aaa.bbb.ccc"


def test_set_token_ignores_a_caller_supplied_session_cookie_and_mints_a_fresh_one(client):
    from app.routers.auth import resolve_auth_token

    # Simulates an attacker planting a known session id in the victim's browser ahead of time
    # (session fixation) - the server must never let a caller dictate its own storage key.
    client.cookies.set("demo_session_id", "attacker-chosen-id")

    response = client.post("/api/auth/token", json={"Token": "aaa.bbb.ccc"})

    new_session_id = response.cookies["demo_session_id"]
    assert new_session_id != "attacker-chosen-id"

    class _AttackerRequest:
        cookies = {"demo_session_id": "attacker-chosen-id"}

    # Falls back to the configured default token (from TNZ_AUTH_TOKEN), not the victim's real
    # override - proving the attacker's known session id never got associated with it.
    assert resolve_auth_token(_AttackerRequest()) != "aaa.bbb.ccc"


def test_set_token_cookie_is_secure_by_default(client, monkeypatch):
    monkeypatch.delenv("TNZ_ALLOW_INSECURE_HTTP", raising=False)

    response = client.post("/api/auth/token", json={"Token": "aaa.bbb.ccc"})

    assert "secure" in response.headers["set-cookie"].lower()


def test_set_token_cookie_omits_secure_when_insecure_http_is_allowed(client, monkeypatch):
    monkeypatch.setenv("TNZ_ALLOW_INSECURE_HTTP", "true")

    response = client.post("/api/auth/token", json={"Token": "aaa.bbb.ccc"})

    assert "secure" not in response.headers["set-cookie"].lower()


def test_token_overrides_are_bounded_and_evict_the_oldest_entry(client, monkeypatch):
    from app.routers import auth

    monkeypatch.setattr(auth, "_TOKEN_OVERRIDES", {})
    monkeypatch.setattr(auth, "_MAX_TOKEN_OVERRIDES", 2)

    # Eviction only has anything to evict when distinct sessions accumulate - a single browser
    # repeatedly calling this endpoint always nets exactly one entry (each call pops its own
    # prior id before adding a new one, per the fixation-prevention fix), so this must simulate
    # independent callers by clearing cookies between calls. Without this, whether the client
    # happens to echo the previous Secure-flagged cookie back over the test's plain http://
    # connection (it doesn't) would silently determine whether this test means anything.
    for i in range(3):
        client.cookies.clear()
        client.post("/api/auth/token", json={"Token": f"aaa.bbb.ccc{i}"})

    assert len(auth._TOKEN_OVERRIDES) == 2
