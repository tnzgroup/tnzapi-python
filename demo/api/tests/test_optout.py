import responses as responses_lib

API_BASE_URL = "https://api.tnz.co.nz/api/v3.00"


@responses_lib.activate
def test_list_optouts(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/optout/list",
        json={"Result": "Success", "ErrorMessage": [], "TotalRecords": 0},
        status=200,
    )

    response = client.get("/api/optout?recordsPerPage=50&page=1")

    assert response.status_code == 200


def test_list_optouts_rejects_an_out_of_range_records_per_page_at_the_query_level(client):
    response = client.get("/api/optout?recordsPerPage=1001&page=1")

    # FastAPI's own Query(ge=1, le=1000) constraint fires before the handler body's
    # validate_pagination() call even runs - proving the bound is enforced at the
    # framework level, not solely by a call that could later be removed/reordered.
    assert response.status_code == 422


def test_list_optouts_rejects_a_non_positive_page_at_the_query_level(client):
    response = client.get("/api/optout?recordsPerPage=50&page=0")

    assert response.status_code == 422


@responses_lib.activate
def test_list_optouts_uses_the_camel_case_records_per_page_value(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/optout/list",
        json={"Result": "Success", "ErrorMessage": [], "TotalRecords": 0},
        status=200,
    )

    client.get("/api/optout?recordsPerPage=99&page=1")

    # Proves the camelCase query param actually reached the SDK call, not just that the
    # response looked fine while silently falling back to the default.
    assert "recordsPerPage=99" in responses_lib.calls[0].request.url


@responses_lib.activate
def test_create_optout(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/optout",
        json={"Result": "Success", "OptOutID": "o-001", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/optout",
        json={"Destination": "+64211111111", "DestType": "SMS", "Notes": "opted out via demo"},
    )

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed == {"Destination": "+64211111111", "DestType": "SMS", "Notes": "opted out via demo"}


@responses_lib.activate
def test_create_optout_returns_400_on_sdk_reported_failure(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/optout",
        json={"Result": "Failed", "ErrorMessage": ["Missing required field: Destination or ContactID"]},
        status=400,
    )

    response = client.post("/api/optout", json={"DestType": "SMS"})

    assert response.status_code == 400


@responses_lib.activate
def test_get_optout_details(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/optout/o-001",
        json={"Result": "Success", "OptOutID": "o-001", "Destination": "+64211111111", "ErrorMessage": []},
        status=200,
    )

    response = client.get("/api/optout/o-001")

    assert response.status_code == 200
    assert response.json()["Destination"] == "+64211111111"


@responses_lib.activate
def test_delete_optout(client):
    responses_lib.add(
        responses_lib.DELETE,
        f"{API_BASE_URL}/optout/o-001",
        json={"Result": "Success", "ErrorMessage": []},
        status=200,
    )

    response = client.delete("/api/optout/o-001")

    assert response.status_code == 200