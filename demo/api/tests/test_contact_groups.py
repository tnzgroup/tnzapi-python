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

    response = client.post("/api/addressbook/contact-groups", json={"ContactID": "c-001", "GroupID": "g-001"})

    assert response.status_code == 200

    import json
    parsed = json.loads(responses_lib.calls[0].request.body)
    assert parsed == {"GroupID": "g-001"}


@responses_lib.activate
def test_list_groups_for_a_contact(client):
    responses_lib.add(
        responses_lib.GET,
        f"{API_BASE_URL}/addressbook/contact/c-001/group/list",
        json={"Result": "Success", "ErrorMessage": [], "Groups": []},
        status=200,
    )

    response = client.get("/api/addressbook/contact-groups?contactID=c-001")

    assert response.status_code == 200


@responses_lib.activate
def test_remove_contact_from_group(client):
    responses_lib.add(
        responses_lib.DELETE,
        f"{API_BASE_URL}/addressbook/contact/c-001/group/g-001",
        json={"Result": "Success", "ErrorMessage": []},
        status=200,
    )

    response = client.delete("/api/addressbook/contact-groups/c-001/g-001")

    assert response.status_code == 200
