import responses as responses_lib

API_BASE_URL = "https://api.tnz.co.nz/api/v3.00"


@responses_lib.activate
def test_send_tts_builds_request_and_returns_success(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/tts",
        json={"Result": "Success", "MessageID": "msg-001", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/tts/send",
        json={"ToNumber": "+64211111111", "MessageToPeople": "Hello"},
    )

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["Destinations"] == [{"ToNumber": "+64211111111"}]
    assert parsed["MessageToPeople"] == "Hello"


@responses_lib.activate
def test_send_tts_translates_dotnet_wire_fields_and_drops_unsupported_ones(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/tts",
        json={"Result": "Success", "MessageID": "msg-002", "ErrorMessage": []},
        status=200,
    )

    client.post(
        "/api/tts/send",
        json={
            "ToNumber": "+64211111111",
            "MessageToPeople": "Hello",
            "TemplateId": "tmpl-1",
            "WebhookCallbackUrl": "https://example.com/hook",
            "CallerId": "+6495005000",
            "SendMode": "Test",
            "ChargeCode": "should-be-dropped",
            "EndCallMessage": "should-be-dropped",
            "Keypads": [{"Tone": 1, "Play": "hi", "RouteNumber": "+64800123123"}],
        },
    )

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["TemplateID"] == "tmpl-1"
    assert parsed["WebhookCallbackURL"] == "https://example.com/hook"
    assert parsed["CallerID"] == "+6495005000"
    assert parsed["Mode"] == "Test"
    assert "ChargeCode" not in parsed
    assert "EndCallMessage" not in parsed
    assert parsed["Keypads"] == [{"Tone": 1, "Play": "hi", "RouteNumber": "+64800123123"}]


@responses_lib.activate
def test_send_tts_returns_400_on_sdk_reported_failure(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/tts",
        json={"Result": "Failed", "ErrorMessage": ["Invalid destination"]},
        status=400,
    )

    response = client.post("/api/tts/send", json={"ToNumber": "bad", "MessageToPeople": "Hi"})

    assert response.status_code == 400
    assert response.json() == {"Result": "Failed", "ErrorMessage": ["Invalid destination"]}


@responses_lib.activate
def test_status_returns_tts_status(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/tts/msg-001",
        json={"Result": "Success", "MessageID": "msg-001", "JobStatus": "Completed"},
        status=200,
    )

    response = client.get("/api/tts/status/msg-001")

    assert response.status_code == 200
    assert response.json()["JobStatus"] == "Completed"


@responses_lib.activate
def test_abort_sends_patch_to_tts_abort_endpoint(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/tts/msg-001/abort",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/tts/msg-001/abort")

    assert response.status_code == 200


@responses_lib.activate
def test_reschedule_sends_patch_with_send_time(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/tts/msg-001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/tts/msg-001/reschedule", json={"SendTime": "2026-08-01T09:00:00"})

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["SendTime"] == "2026-08-01T09:00:00"


@responses_lib.activate
def test_resubmit_sends_patch_with_send_time(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/tts/msg-001/resubmit",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/tts/msg-001/resubmit", json={"SendTime": "2026-08-01T09:00:00"})

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["SendTime"] == "2026-08-01T09:00:00"


@responses_lib.activate
def test_pacing_sends_patch_with_number_of_operators(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/tts/msg-001/pacing",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Result": "Success"},
        status=200,
    )

    response = client.patch("/api/tts/msg-001/pacing", json={"NumberOfOperators": 5})

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["NumberOfOperators"] == 5


def test_pacing_rejects_a_number_of_operators_below_one(client):
    response = client.patch("/api/tts/msg-001/pacing", json={"NumberOfOperators": 0})

    assert response.status_code == 422


def test_pacing_rejects_a_number_of_operators_above_99999(client):
    response = client.patch("/api/tts/msg-001/pacing", json={"NumberOfOperators": 100000})

    assert response.status_code == 422
