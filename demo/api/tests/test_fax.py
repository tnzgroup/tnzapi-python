import responses as responses_lib

API_BASE_URL = "https://api.tnz.co.nz/api/v3.00"


@responses_lib.activate
def test_send_fax_builds_request_and_returns_success(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/fax",
        json={"Result": "Success", "MessageID": "msg-001", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/fax/send",
        json={"ToNumber": "+6491111111", "Attachments": [{"FileName": "doc.pdf", "FileContent": "aGVsbG8="}]},
    )

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["Destinations"] == [{"ToNumber": "+6491111111"}]
    assert parsed["Files"] == [{"Name": "doc.pdf", "Data": "aGVsbG8="}]


@responses_lib.activate
def test_send_fax_with_attachment_emits_no_deprecation_warning(client, recwarn):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/fax",
        json={"Result": "Success", "MessageID": "msg-001", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/fax/send",
        json={"ToNumber": "+6491111111", "Attachments": [{"FileName": "doc.pdf", "FileContent": "aGVsbG8="}]},
    )

    assert response.status_code == 200
    assert not any(issubclass(w.category, DeprecationWarning) for w in recwarn)


@responses_lib.activate
def test_send_fax_translates_dotnet_wire_fields_to_tnzapi_python_field_names(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/fax",
        json={"Result": "Success", "MessageID": "msg-002", "ErrorMessage": []},
        status=200,
    )

    client.post(
        "/api/fax/send",
        json={
            "ToNumber": "+6491111111",
            "TemplateId": "tmpl-1",
            "WebhookCallbackUrl": "https://example.com/hook",
            "Csid": "MyFax",
            "SendMode": "Test",
            "ChargeCode": "should-be-dropped",
        },
    )

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["TemplateID"] == "tmpl-1"
    assert parsed["WebhookCallbackURL"] == "https://example.com/hook"
    assert parsed["CSID"] == "MyFax"
    assert parsed["Mode"] == "Test"
    assert "ChargeCode" not in parsed


@responses_lib.activate
def test_send_fax_returns_400_on_sdk_reported_failure(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/fax",
        json={"Result": "Failed", "ErrorMessage": ["Invalid destination"]},
        status=400,
    )

    response = client.post("/api/fax/send", json={"ToNumber": "bad", "TemplateId": "11111111-1111-1111-1111-111111111111"})

    assert response.status_code == 400
    assert response.json() == {"Result": "Failed", "ErrorMessage": ["Invalid destination"]}


@responses_lib.activate
def test_status_returns_fax_status(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/fax/msg-001",
        json={"Result": "Success", "MessageID": "msg-001", "JobStatus": "Completed"},
        status=200,
    )

    response = client.get("/api/fax/status/msg-001")

    assert response.status_code == 200
    assert response.json()["JobStatus"] == "Completed"


def test_send_fax_rejects_non_base64_attachment_content(client):
    response = client.post(
        "/api/fax/send",
        json={"ToNumber": "+6491111111", "Attachments": [{"FileName": "doc.pdf", "FileContent": "not valid!!"}]},
    )

    assert response.status_code == 422


def test_send_fax_rejects_more_than_the_max_attachment_count(client):
    from app.attachments import MAX_ATTACHMENT_COUNT

    response = client.post(
        "/api/fax/send",
        json={
            "ToNumber": "+6491111111",
            "Attachments": [
                {"FileName": f"a{i}.pdf", "FileContent": "aGVsbG8="} for i in range(MAX_ATTACHMENT_COUNT + 1)
            ],
        },
    )

    assert response.status_code == 422


@responses_lib.activate
def test_abort_sends_patch_to_fax_abort_endpoint(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/fax/msg-001/abort",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/fax/msg-001/abort")

    assert response.status_code == 200


@responses_lib.activate
def test_reschedule_sends_patch_with_send_time(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/fax/msg-001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/fax/msg-001/reschedule", json={"SendTime": "2026-08-01T09:00:00"})

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["SendTime"] == "2026-08-01T09:00:00"


@responses_lib.activate
def test_resubmit_sends_patch_with_send_time(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/fax/msg-001/resubmit",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/fax/msg-001/resubmit", json={"SendTime": "2026-08-01T09:00:00"})

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["SendTime"] == "2026-08-01T09:00:00"
