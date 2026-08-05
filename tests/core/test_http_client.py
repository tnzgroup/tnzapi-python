import json

import responses as responses_lib
from tnzapi.core.auth import TNZApiUser
from tnzapi.core.http_client import HttpClient
from tests.conftest import mock_endpoint


@responses_lib.activate
def test_get_sends_bearer_header():
    user = TNZApiUser(auth_token="tok123")
    client = HttpClient(user)

    mock_endpoint(
        responses_lib.GET,
        "/sms/msg1",
        json={"Result": "Success", "MessageID": "msg1"},
        status=200,
    )

    r = client.get("/sms/msg1")

    assert r.status_code == 200
    sent_headers = responses_lib.calls[0].request.headers
    assert sent_headers["Authorization"] == "Bearer tok123"
    assert sent_headers["Content-Type"] == "application/json"
    assert sent_headers["Accept"] == "application/json"


@responses_lib.activate
def test_post_sends_json_body():
    user = TNZApiUser(auth_token="tok123")
    client = HttpClient(user)

    mock_endpoint(
        responses_lib.POST,
        "/sms",
        json={"MessageID": "msg1"},
        status=200,
    )

    r = client.post("/sms", {"Message": "hi"})

    assert r.status_code == 200
    assert json.loads(responses_lib.calls[0].request.body) == {"Message": "hi"}


def test_refuses_plain_http_without_override(monkeypatch):
    monkeypatch.delenv("TNZ_ALLOW_INSECURE_HTTP", raising=False)
    user = TNZApiUser(auth_token="tok123", base_url="http://insecure.example.com")
    client = HttpClient(user)

    import pytest
    with pytest.raises(ValueError, match="HTTPS"):
        client.get("/sms/msg1")


@responses_lib.activate
def test_patch_sends_json_body():
    user = TNZApiUser(auth_token="tok123")
    client = HttpClient(user)

    mock_endpoint(
        responses_lib.PATCH,
        "/sms/msg1/reschedule",
        json={"Result": "Success"},
        status=200,
    )

    r = client.patch("/sms/msg1/reschedule", {"SendTime": "2026-07-20T12:00:00Z"})

    assert r.status_code == 200
    assert json.loads(responses_lib.calls[0].request.body) == {"SendTime": "2026-07-20T12:00:00Z"}


@responses_lib.activate
def test_delete_sends_headers():
    user = TNZApiUser(auth_token="tok123")
    client = HttpClient(user)

    mock_endpoint(
        responses_lib.DELETE,
        "/sms/msg1",
        json={"Result": "Success"},
        status=200,
    )

    r = client.delete("/sms/msg1")

    assert r.status_code == 200
    sent_headers = responses_lib.calls[0].request.headers
    assert sent_headers["Authorization"] == "Bearer tok123"
    assert sent_headers["Content-Type"] == "application/json"
    assert sent_headers["Accept"] == "application/json"
