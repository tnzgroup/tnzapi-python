import responses as responses_lib

API_BASE_URL = "https://api.tnz.co.nz/api/v3.00"


@responses_lib.activate
def test_send_voice_builds_request_and_returns_success(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/voice",
        json={"Result": "Success", "MessageID": "msg-001", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/voice/send",
        json={"ToNumber": "+64211111111", "MessageToPeople": "base64audiodata"},
    )

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["Destinations"] == [{"ToNumber": "+64211111111"}]
    assert parsed["MessageToPeople"] == "base64audiodata"


@responses_lib.activate
def test_send_voice_accepts_missing_message_to_people_when_template_id_given(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/voice",
        json={"Result": "Success", "MessageID": "msg-002", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/voice/send",
        json={"ToNumber": "+64211111111", "TemplateId": "tmpl-1"},
    )

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["TemplateID"] == "tmpl-1"
    assert "MessageToPeople" not in parsed


@responses_lib.activate
def test_send_voice_translates_dotnet_wire_fields_and_drops_unsupported_ones(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/voice",
        json={"Result": "Success", "MessageID": "msg-003", "ErrorMessage": []},
        status=200,
    )

    client.post(
        "/api/voice/send",
        json={
            "ToNumber": "+64211111111",
            "MessageToPeople": "base64audiodata",
            "CallerId": "+6495005000",
            "SendMode": "Test",
            "ChargeCode": "should-be-dropped",
            "EndCallMessage": "should-be-dropped",
        },
    )

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["CallerID"] == "+6495005000"
    assert parsed["Mode"] == "Test"
    assert "ChargeCode" not in parsed
    assert "EndCallMessage" not in parsed


@responses_lib.activate
def test_status_returns_voice_status(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/voice/msg-001",
        json={"Result": "Success", "MessageID": "msg-001", "JobStatus": "Completed"},
        status=200,
    )

    response = client.get("/api/voice/status/msg-001")

    assert response.status_code == 200
    assert response.json()["JobStatus"] == "Completed"


@responses_lib.activate
def test_abort_sends_patch_to_voice_abort_endpoint(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/voice/msg-001/abort",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/voice/msg-001/abort")

    assert response.status_code == 200


@responses_lib.activate
def test_reschedule_sends_patch_with_send_time(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/voice/msg-001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/voice/msg-001/reschedule", json={"SendTime": "2026-08-01T09:00:00"})

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["SendTime"] == "2026-08-01T09:00:00"


@responses_lib.activate
def test_resubmit_sends_patch_with_send_time(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/voice/msg-001/resubmit",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/voice/msg-001/resubmit", json={"SendTime": "2026-08-01T09:00:00"})

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["SendTime"] == "2026-08-01T09:00:00"


@responses_lib.activate
def test_pacing_sends_patch_with_number_of_operators(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/voice/msg-001/pacing",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/voice/msg-001/pacing", json={"NumberOfOperators": 5})

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["NumberOfOperators"] == 5
