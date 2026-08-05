import responses as responses_lib

API_BASE_URL = "https://api.tnz.co.nz/api/v3.00"


@responses_lib.activate
def test_send_workflow_builds_a_single_omni_channel_destination(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/workflow",
        json={"Result": "Success", "MessageID": "msg-001", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/workflow/send",
        json={
            "WorkflowTemplateId": "tmpl-1",
            "ToNumber": "+64211111111",
            "MainPhone": "+6491111111",
            "EmailAddress": "a@example.com",
        },
    )

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["WorkflowTemplateID"] == "tmpl-1"
    assert parsed["Destinations"] == [
        {"ToNumber": "+64211111111", "MainPhone": "+6491111111", "EmailAddress": "a@example.com"}
    ]


@responses_lib.activate
def test_send_workflow_splits_comma_separated_contact_and_group_ids_into_extra_destinations(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/workflow",
        json={"Result": "Success", "MessageID": "msg-002", "ErrorMessage": []},
        status=200,
    )

    client.post(
        "/api/workflow/send",
        json={
            "WorkflowTemplateId": "tmpl-1",
            "ContactIds": "contact-1, contact-2",
            "GroupIds": "group-1",
        },
    )

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert {"ContactID": "contact-1"} in parsed["Destinations"]
    assert {"ContactID": "contact-2"} in parsed["Destinations"]
    assert {"GroupID": "group-1"} in parsed["Destinations"]


@responses_lib.activate
def test_send_workflow_translates_dotnet_wire_fields_and_drops_charge_code(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/workflow",
        json={"Result": "Success", "MessageID": "msg-003", "ErrorMessage": []},
        status=200,
    )

    client.post(
        "/api/workflow/send",
        json={
            "WorkflowTemplateId": "tmpl-1",
            "ToNumber": "+64211111111",
            "WebhookCallbackUrl": "https://example.com/hook",
            "ChargeCode": "should-be-dropped",
        },
    )

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed["WebhookCallbackURL"] == "https://example.com/hook"
    assert "ChargeCode" not in parsed


def test_send_workflow_rejects_send_mode_since_it_has_no_effect(client):
    response = client.post(
        "/api/workflow/send",
        json={"WorkflowTemplateId": "tmpl-1", "ToNumber": "+64211111111", "SendMode": "Test"},
    )

    assert response.status_code == 400
    assert response.json()["Result"] == "Failed"


def test_send_workflow_rejects_a_request_with_no_destination_at_all(client):
    response = client.post("/api/workflow/send", json={"WorkflowTemplateId": "tmpl-1"})

    assert response.status_code == 400
    assert response.json()["Result"] == "Failed"


@responses_lib.activate
def test_send_workflow_returns_400_on_sdk_reported_failure(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/workflow",
        json={"Result": "Failed", "ErrorMessage": ["Missing required field: WorkflowTemplateID"]},
        status=400,
    )

    response = client.post("/api/workflow/send", json={"WorkflowTemplateId": "", "ToNumber": "+64211111111"})

    assert response.status_code == 400
