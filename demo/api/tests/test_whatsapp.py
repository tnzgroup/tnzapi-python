import json

import responses as responses_lib

API_BASE_URL = "https://api.tnz.co.nz/api/v3.00"


@responses_lib.activate
def test_send_whatsapp_builds_request_and_returns_success(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/whatsapp",
        json={"Result": "Success", "MessageID": "msg-001", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/whatsapp/send",
        json={"ToNumber": "+64211111111", "Message": "Hi", "TemplateId": "tmpl-1", "FromNumber": "+6495005000"},
    )

    assert response.status_code == 200

    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["Destinations"] == [{"ToNumber": "+64211111111"}]
    assert parsed["TemplateID"] == "tmpl-1"
    assert parsed["FromNumber"] == "+6495005000"


@responses_lib.activate
def test_send_whatsapp_with_attachment_builds_correct_wire_body_and_emits_no_warning(client, recwarn):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/whatsapp",
        json={"Result": "Success", "MessageID": "msg-001", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/whatsapp/send",
        json={
            "ToNumber": "+64211234567",
            "Message": "Hi",
            "TemplateId": "tmpl-1",
            "FromNumber": "+6495006000",
            "Attachments": [{"FileName": "a.txt", "FileContent": "aGVsbG8="}],
        },
    )

    assert response.status_code == 200
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["Files"] == [{"Name": "a.txt", "Data": "aGVsbG8="}]
    assert not any(issubclass(w.category, DeprecationWarning) for w in recwarn)


@responses_lib.activate
def test_send_whatsapp_puts_custom_fields_on_the_destination_not_the_top_level(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/whatsapp",
        json={"Result": "Success", "MessageID": "msg-002", "ErrorMessage": []},
        status=200,
    )

    client.post(
        "/api/whatsapp/send",
        json={
            "ToNumber": "+64211111111",
            "Message": "Hi",
            "TemplateId": "tmpl-1",
            "FromNumber": "+6495005000",
            "Custom1": "John",
            "Custom2": "Doe",
            "ReportTo": "should-be-dropped@example.com",
            "ChargeCode": "should-be-dropped",
            "FallbackMode": ["RCS"],
        },
    )

    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["Destinations"] == [{"ToNumber": "+64211111111", "Custom1": "John", "Custom2": "Doe"}]
    assert parsed["FallbackMode"] == "RCS"
    assert "ReportTo" not in parsed
    assert "ChargeCode" not in parsed


@responses_lib.activate
def test_send_whatsapp_returns_400_on_sdk_reported_failure(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/whatsapp",
        json={"Result": "Failed", "ErrorMessage": ["Template not approved for this account"]},
        status=400,
    )

    response = client.post(
        "/api/whatsapp/send",
        json={
            "ToNumber": "+64211111111",
            "Message": "Hi",
            "TemplateId": "tmpl-1",
            "FromNumber": "+6495005000",
        },
    )

    assert response.status_code == 400


def test_send_whatsapp_rejects_missing_template_id_before_reaching_the_sdk(client):
    # TemplateId/FromNumber are required by WhatsApp.SendMessage() itself - the Pydantic model
    # marks them required too (matching ToNumber/Message's existing required status), so a
    # missing one 422s locally instead of round-tripping to the SDK/API first.
    response = client.post(
        "/api/whatsapp/send",
        json={"ToNumber": "+64211111111", "Message": "Hi", "FromNumber": "+6495005000"},
    )

    assert response.status_code == 422


def test_send_whatsapp_rejects_missing_from_number_before_reaching_the_sdk(client):
    response = client.post(
        "/api/whatsapp/send",
        json={"ToNumber": "+64211111111", "Message": "Hi", "TemplateId": "tmpl-1"},
    )

    assert response.status_code == 422


@responses_lib.activate
def test_status_returns_whatsapp_status(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/whatsapp/msg-001",
        json={"Result": "Success", "MessageID": "msg-001", "JobStatus": "Completed"},
        status=200,
    )

    response = client.get("/api/whatsapp/status/msg-001")

    assert response.status_code == 200
    assert response.json()["JobStatus"] == "Completed"


@responses_lib.activate
def test_received_returns_whatsapp_received_messages(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/whatsapp/received",
        json={"Result": "Success", "ErrorMessage": [], "TotalRecords": 0},
        status=200,
    )

    response = client.get("/api/whatsapp/received?timePeriod=1440&recordsPerPage=100&page=1")

    assert response.status_code == 200

    # Proves the camelCase query params actually reached the SDK call, not just that the
    # response looked fine while silently falling back to defaults/None.
    assert "timePeriod=1440" in responses_lib.calls[0].request.url


@responses_lib.activate
def test_send_whatsapp_accepts_multiple_fallback_mode_values(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/whatsapp",
        json={"Result": "Success", "MessageID": "msg-004", "ErrorMessage": []},
        status=200,
    )

    client.post(
        "/api/whatsapp/send",
        json={
            "ToNumber": "+64211111111",
            "Message": "Hi",
            "TemplateId": "tmpl-1",
            "FromNumber": "+6495005000",
            "FallbackMode": ["RCS", "SMS"],
        },
    )

    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["FallbackMode"] == "RCS, SMS"


def test_send_whatsapp_rejects_non_base64_attachment_content(client):
    response = client.post(
        "/api/whatsapp/send",
        json={
            "ToNumber": "+64211111111",
            "Message": "Hi",
            "TemplateId": "tmpl-1",
            "FromNumber": "+6495005000",
            "Attachments": [{"FileName": "a.txt", "FileContent": "not valid base64!!"}],
        },
    )

    assert response.status_code == 422


def test_send_whatsapp_rejects_more_than_the_max_attachment_count(client):
    from app.attachments import MAX_ATTACHMENT_COUNT

    response = client.post(
        "/api/whatsapp/send",
        json={
            "ToNumber": "+64211111111",
            "Message": "Hi",
            "TemplateId": "tmpl-1",
            "FromNumber": "+6495005000",
            "Attachments": [
                {"FileName": f"a{i}.txt", "FileContent": "aGVsbG8="} for i in range(MAX_ATTACHMENT_COUNT + 1)
            ],
        },
    )

    assert response.status_code == 422


@responses_lib.activate
def test_abort_sends_patch_to_whatsapp_abort_endpoint(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/whatsapp/msg-001/abort",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/whatsapp/msg-001/abort")

    assert response.status_code == 200


@responses_lib.activate
def test_reschedule_sends_patch_with_send_time(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/whatsapp/msg-001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/whatsapp/msg-001/reschedule", json={"SendTime": "2026-08-01T09:00:00"})

    assert response.status_code == 200

    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["SendTime"] == "2026-08-01T09:00:00"
