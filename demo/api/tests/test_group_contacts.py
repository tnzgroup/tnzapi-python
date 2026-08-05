import responses as responses_lib

API_BASE_URL = "https://api.tnz.co.nz/api/v3.00"


@responses_lib.activate
def test_add_contact_to_group(client):
    responses_lib.add(
        responses_lib.PATCH,
        f"{API_BASE_URL}/addressbook/contact/c-001/group",
        json={"Result": "Success", "ErrorMessage": []},
        status=200,
    )

    response = client.post("/api/addressbook/group-contacts", json={"GroupID": "g-001", "ContactID": "c-001"})

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed == {"GroupID": "g-001"}


@responses_lib.activate
def test_list_contacts_for_a_group(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/addressbook/group/g-001/contact/list",
        json={"Result": "Success", "ErrorMessage": [], "Contacts": []},
        status=200,
    )

    response = client.get("/api/addressbook/group-contacts?groupID=g-001")

    assert response.status_code == 200


@responses_lib.activate
def test_remove_contact_from_group(client):
    responses_lib.add(
        responses_lib.DELETE,
        f"{API_BASE_URL}/addressbook/contact/c-001/group/g-001",
        json={"Result": "Success", "ErrorMessage": []},
        status=200,
    )

    response = client.delete("/api/addressbook/group-contacts/g-001/c-001")

    assert response.status_code == 200
