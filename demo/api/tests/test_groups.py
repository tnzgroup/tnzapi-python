import responses as responses_lib

API_BASE_URL = "https://api.tnz.co.nz/api/v3.00"


@responses_lib.activate
def test_list_groups(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/addressbook/group/list",
        json={"Result": "Success", "ErrorMessage": [], "TotalRecords": 0, "Groups": []},
        status=200,
    )

    response = client.get("/api/addressbook/groups?recordsPerPage=50&page=1")

    assert response.status_code == 200


@responses_lib.activate
def test_list_groups_uses_the_camel_case_records_per_page_value(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/addressbook/group/list",
        json={"Result": "Success", "ErrorMessage": [], "TotalRecords": 0, "Groups": []},
        status=200,
    )

    client.get("/api/addressbook/groups?recordsPerPage=99&page=1")

    # Proves the camelCase query param actually reached the SDK call, not just that the
    # response looked fine while silently falling back to the default.
    assert "recordsPerPage=99" in responses_lib.calls[0].request.url


@responses_lib.activate
def test_create_group(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/addressbook/group",
        json={"Result": "Success", "GroupID": "g-001", "ErrorMessage": []},
        status=200,
    )

    response = client.post("/api/addressbook/groups", json={"GroupName": "Sales Team", "ViewEditBy": "Account"})

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed == {"GroupName": "Sales Team", "ViewEditBy": "Account"}


@responses_lib.activate
def test_get_group_detail(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/addressbook/group/g-001",
        json={"Result": "Success", "GroupID": "g-001", "GroupName": "Sales Team", "ErrorMessage": []},
        status=200,
    )

    response = client.get("/api/addressbook/groups/g-001")

    assert response.status_code == 200
    assert response.json()["GroupName"] == "Sales Team"


@responses_lib.activate
def test_update_group_only_sends_the_fields_provided(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/addressbook/group/g-001",
        json={"Result": "Success", "GroupID": "g-001", "ErrorMessage": []},
        status=200,
    )

    response = client.put("/api/addressbook/groups/g-001", json={"GroupName": "New Name"})

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed == {"GroupName": "New Name"}


@responses_lib.activate
def test_delete_group(client):
    responses_lib.add(
        responses_lib.DELETE,
        f"{API_BASE_URL}/addressbook/group/g-001",
        json={"Result": "Success", "ErrorMessage": []},
        status=200,
    )

    response = client.delete("/api/addressbook/groups/g-001")

    assert response.status_code == 200
