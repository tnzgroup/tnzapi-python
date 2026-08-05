import responses as responses_lib

API_BASE_URL = "https://api.tnz.co.nz/api/v3.00"


@responses_lib.activate
def test_send_rcs_builds_request_and_returns_success(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/rcs",
        json={"Result": "Success", "MessageID": "msg-001", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/rcs/send",
        json={"ToNumber": "+64211111111", "Message": "Hello"},
    )

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["Destinations"] == [{"ToNumber": "+64211111111"}]
    assert parsed["Message"] == "Hello"


@responses_lib.activate
def test_send_rcs_translates_dotnet_wire_fields_and_drops_report_to(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/rcs",
        json={"Result": "Success", "MessageID": "msg-002", "ErrorMessage": []},
        status=200,
    )

    client.post(
        "/api/rcs/send",
        json={
            "ToNumber": "+64211111111",
            "Message": "Hello",
            "TemplateId": "tmpl-1",
            "WebhookCallbackUrl": "https://example.com/hook",
            "SmsEmailReply": "reply@example.com",
            "SendMode": "Test",
            "ReportTo": "should-be-dropped@example.com",
            "ChargeCode": "should-be-dropped",
            "CharacterConversion": True,
            "Attachments": [{"FileName": "a.txt", "FileContent": "aGVsbG8="}],
        },
    )

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["TemplateID"] == "tmpl-1"
    assert parsed["WebhookCallbackURL"] == "https://example.com/hook"
    assert parsed["SMSEmailReply"] == "reply@example.com"
    assert parsed["Mode"] == "Test"
    assert parsed["Files"] == [{"Name": "a.txt", "Data": "aGVsbG8="}]
    assert parsed["CharacterConversion"] is True
    assert "ReportTo" not in parsed
    assert "ChargeCode" not in parsed


@responses_lib.activate
def test_send_rcs_with_attachment_emits_no_deprecation_warning(client, recwarn):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/rcs",
        json={"Result": "Success", "MessageID": "msg-001", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/rcs/send",
        json={
            "ToNumber": "+64211111111",
            "Message": "Hello",
            "Attachments": [{"FileName": "a.txt", "FileContent": "aGVsbG8="}],
        },
    )

    assert response.status_code == 200
    assert not any(issubclass(w.category, DeprecationWarning) for w in recwarn)


@responses_lib.activate
def test_send_rcs_returns_400_on_sdk_reported_failure(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/rcs",
        json={"Result": "Failed", "ErrorMessage": ["Invalid destination"]},
        status=400,
    )

    response = client.post("/api/rcs/send", json={"ToNumber": "bad", "Message": "hi"})

    assert response.status_code == 400


@responses_lib.activate
def test_status_returns_rcs_status(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/rcs/msg-001",
        json={"Result": "Success", "MessageID": "msg-001", "JobStatus": "Completed"},
        status=200,
    )

    response = client.get("/api/rcs/status/msg-001")

    assert response.status_code == 200
    assert response.json()["JobStatus"] == "Completed"


@responses_lib.activate
def test_received_returns_rcs_received_messages(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/rcs/received",
        json={"Result": "Success", "ErrorMessage": [], "TotalRecords": 0},
        status=200,
    )

    response = client.get("/api/rcs/received?timePeriod=1440&recordsPerPage=100&page=1")

    assert response.status_code == 200

    # Proves the camelCase query params actually reached the SDK call, not just that the
    # response looked fine while silently falling back to defaults/None.
    assert "timePeriod=1440" in responses_lib.calls[0].request.url


@responses_lib.activate
def test_send_rcs_accepts_multiple_fallback_mode_values(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/rcs",
        json={"Result": "Success", "MessageID": "msg-004", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/rcs/send",
        json={"ToNumber": "+64211111111", "Message": "Hello", "FallbackMode": ["Voice", "SMS"]},
    )

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["FallbackMode"] == "Voice, SMS"


def test_send_rcs_rejects_non_base64_attachment_content(client):
    response = client.post(
        "/api/rcs/send",
        json={
            "ToNumber": "+64211111111",
            "Message": "Hello",
            "Attachments": [{"FileName": "a.txt", "FileContent": "not valid base64!!"}],
        },
    )

    assert response.status_code == 422


def test_send_rcs_rejects_more_than_the_max_attachment_count(client):
    from app.attachments import MAX_ATTACHMENT_COUNT

    response = client.post(
        "/api/rcs/send",
        json={
            "ToNumber": "+64211111111",
            "Message": "Hello",
            "Attachments": [
                {"FileName": f"a{i}.txt", "FileContent": "aGVsbG8="} for i in range(MAX_ATTACHMENT_COUNT + 1)
            ],
        },
    )

    assert response.status_code == 422


@responses_lib.activate
def test_abort_sends_patch_to_rcs_abort_endpoint(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/rcs/msg-001/abort",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/rcs/msg-001/abort")

    assert response.status_code == 200


@responses_lib.activate
def test_reschedule_sends_patch_with_send_time(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/rcs/msg-001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/rcs/msg-001/reschedule", json={"SendTime": "2026-08-01T09:00:00"})

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["SendTime"] == "2026-08-01T09:00:00"
