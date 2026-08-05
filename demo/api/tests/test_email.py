import json

import responses as responses_lib

API_BASE_URL = "https://api.tnz.co.nz/api/v3.00"


@responses_lib.activate
def test_send_email_builds_request_and_returns_success(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/email",
        json={"Result": "Success", "MessageID": "msg-001", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/email/send",
        json={"EmailAddress": "a@example.com", "Subject": "Hi", "MessageHtml": "<p>Hi</p>"},
    )

    assert response.status_code == 200

    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["Destinations"] == [{"EmailAddress": "a@example.com"}]
    assert parsed["EmailSubject"] == "Hi"
    assert parsed["MessageHTML"] == "<p>Hi</p>"


@responses_lib.activate
def test_send_email_accepts_message_plain_without_message_html(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/email",
        json={"Result": "Success", "MessageID": "msg-001", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/email/send",
        json={"EmailAddress": "a@example.com", "Subject": "Hi", "MessagePlain": "Hi world!"},
    )

    assert response.status_code == 200

    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["MessagePlain"] == "Hi world!"
    assert "MessageHTML" not in parsed


@responses_lib.activate
def test_send_email_translates_bcc_email_field_name(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/email",
        json={"Result": "Success", "MessageID": "msg-001", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/email/send",
        json={
            "EmailAddress": "a@example.com",
            "Subject": "Hi",
            "MessageHtml": "<p>Hi</p>",
            "BccEmail": "hidden@example.com",
        },
    )

    assert response.status_code == 200

    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["BCCEmail"] == "hidden@example.com"


@responses_lib.activate
def test_send_email_translates_dotnet_wire_fields_to_tnzapi_python_field_names(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/email",
        json={"Result": "Success", "MessageID": "msg-002", "ErrorMessage": []},
        status=200,
    )

    client.post(
        "/api/email/send",
        json={
            "EmailAddress": "a@example.com",
            "Subject": "Hi",
            "MessageHtml": "<p>Hi</p>",
            "TemplateId": "tmpl-1",
            "CcEmail": "cc@example.com",
            "WebhookCallbackUrl": "https://example.com/hook",
            "SendMode": "Test",
            "SmtpFrom": "should-be-dropped@example.com",
            "ChargeCode": "should-be-dropped",
            "Attachments": [{"FileName": "a.txt", "FileContent": "aGVsbG8="}],
        },
    )

    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["TemplateID"] == "tmpl-1"
    assert parsed["CCEmail"] == "cc@example.com"
    assert parsed["WebhookCallbackURL"] == "https://example.com/hook"
    assert parsed["Mode"] == "Test"
    assert parsed["Files"] == [{"Name": "a.txt", "Data": "aGVsbG8="}]
    assert "SmtpFrom" not in parsed
    assert "ChargeCode" not in parsed


@responses_lib.activate
def test_send_email_with_attachment_emits_no_deprecation_warning(client, recwarn):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/email",
        json={"Result": "Success", "MessageID": "msg-001", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/email/send",
        json={
            "EmailAddress": "a@example.com",
            "Subject": "Hi",
            "MessageHtml": "<p>Hi</p>",
            "Attachments": [{"FileName": "a.txt", "FileContent": "aGVsbG8="}],
        },
    )

    assert response.status_code == 200
    assert not any(issubclass(w.category, DeprecationWarning) for w in recwarn)


@responses_lib.activate
def test_send_email_returns_400_on_sdk_reported_failure(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/email",
        json={"Result": "Failed", "ErrorMessage": ["Invalid address"]},
        status=400,
    )

    response = client.post("/api/email/send", json={"EmailAddress": "bad", "Subject": "Hi", "MessageHtml": "Hi"})

    assert response.status_code == 400
    assert response.json() == {"Result": "Failed", "ErrorMessage": ["Invalid address"]}


@responses_lib.activate
def test_status_returns_email_status(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/email/msg-001",
        json={"Result": "Success", "MessageID": "msg-001", "JobStatus": "Completed"},
        status=200,
    )

    response = client.get("/api/email/status/msg-001")

    assert response.status_code == 200
    assert response.json()["JobStatus"] == "Completed"


def test_send_email_rejects_non_base64_attachment_content(client):
    response = client.post(
        "/api/email/send",
        json={
            "EmailAddress": "a@example.com",
            "Subject": "Hi",
            "MessageHtml": "Hi",
            "Attachments": [{"FileName": "a.txt", "FileContent": "not valid base64!!"}],
        },
    )

    assert response.status_code == 422


def test_send_email_rejects_more_than_the_max_attachment_count(client):
    from app.attachments import MAX_ATTACHMENT_COUNT

    response = client.post(
        "/api/email/send",
        json={
            "EmailAddress": "a@example.com",
            "Subject": "Hi",
            "MessageHtml": "Hi",
            "Attachments": [
                {"FileName": f"a{i}.txt", "FileContent": "aGVsbG8="} for i in range(MAX_ATTACHMENT_COUNT + 1)
            ],
        },
    )

    assert response.status_code == 422


@responses_lib.activate
def test_abort_sends_patch_to_email_abort_endpoint(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/email/msg-001/abort",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/email/msg-001/abort")

    assert response.status_code == 200


@responses_lib.activate
def test_reschedule_sends_patch_with_send_time(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/email/msg-001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/email/msg-001/reschedule", json={"SendTime": "2026-08-01T09:00:00"})

    assert response.status_code == 200

    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["SendTime"] == "2026-08-01T09:00:00"


@responses_lib.activate
def test_resubmit_sends_patch_with_send_time(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/email/msg-001/resubmit",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/email/msg-001/resubmit", json={"SendTime": "2026-08-01T09:00:00"})

    assert response.status_code == 200

    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["SendTime"] == "2026-08-01T09:00:00"
