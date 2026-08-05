import responses as responses_lib

API_BASE_URL = "https://api.tnz.co.nz/api/v3.00"


@responses_lib.activate
def test_list_contacts(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/addressbook/contact/list",
        json={"Result": "Success", "ErrorMessage": [], "TotalRecords": 0, "Contacts": []},
        status=200,
    )

    response = client.get("/api/addressbook/contacts?recordsPerPage=50&page=1")

    assert response.status_code == 200


@responses_lib.activate
def test_list_contacts_uses_the_camel_case_records_per_page_value(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/addressbook/contact/list",
        json={"Result": "Success", "ErrorMessage": [], "TotalRecords": 0, "Contacts": []},
        status=200,
    )

    client.get("/api/addressbook/contacts?recordsPerPage=99&page=1")

    # Proves the camelCase query param actually reached the SDK call, not just that the
    # response looked fine while silently falling back to the default.
    assert "recordsPerPage=99" in responses_lib.calls[0].request.url


@responses_lib.activate
def test_create_contact(client):
    responses_lib.add(
        responses_lib.POST,
        f"{API_BASE_URL}/addressbook/contact",
        json={"Result": "Success", "ContactID": "c-001", "ErrorMessage": []},
        status=200,
    )

    response = client.post(
        "/api/addressbook/contacts",
        json={"FirstName": "John", "LastName": "Doe", "EmailAddress": "john@example.com"},
    )

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed == {"FirstName": "John", "LastName": "Doe", "EmailAddress": "john@example.com"}


@responses_lib.activate
def test_get_contact_detail(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/addressbook/contact/c-001",
        json={"Result": "Success", "ContactID": "c-001", "FirstName": "John", "ErrorMessage": []},
        status=200,
    )

    response = client.get("/api/addressbook/contacts/c-001")

    assert response.status_code == 200
    assert response.json()["FirstName"] == "John"


@responses_lib.activate
def test_update_contact_only_sends_the_fields_provided(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/addressbook/contact/c-001",
        json={"Result": "Success", "ContactID": "c-001", "ErrorMessage": []},
        status=200,
    )

    response = client.put("/api/addressbook/contacts/c-001", json={"LastName": "Smith"})

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed == {"LastName": "Smith"}


@responses_lib.activate
def test_delete_contact(client):
    responses_lib.add(
        responses_lib.DELETE,
        f"{API_BASE_URL}/addressbook/contact/c-001",
        json={"Result": "Success", "ErrorMessage": []},
        status=200,
    )

    response = client.delete("/api/addressbook/contacts/c-001")

    assert response.status_code == 200
