import json
import warnings
from urllib.parse import parse_qs, urlparse

import pytest
import responses as responses_lib

from tnzapi.api.v300.addressbook.builders.contact import Contact
from tnzapi.api.v300.addressbook.models.requests.contact_request import ContactRequest
from tnzapi.api.v300.addressbook.models.responses.contact_response import ContactResponse
from tests.conftest import mock_endpoint


def test_set_applies_known_fields(api_user):
    contact = Contact(api_user)
    contact.Set(FirstName="Jane", LastName="Doe")

    assert contact.FirstName == "Jane"
    assert contact.LastName == "Doe"


def test_set_raises_on_unknown_field(api_user):
    contact = Contact(api_user)

    with pytest.raises(ValueError):
        contact.Set(Bogus="x")


def test_set_is_chainable(api_user):
    contact = Contact(api_user)

    assert contact.Set(FirstName="Jane") is contact


def test_build_returns_independent_copy(api_user):
    contact = Contact(api_user)
    contact.Set(FirstName="Jane", EmailAddress="jane@example.com")

    model = contact.Build()

    assert isinstance(model, ContactRequest)
    assert model.FirstName == "Jane"

    contact.Set(FirstName="Changed")
    assert model.FirstName == "Jane"


@responses_lib.activate
def test_create_dispatches_post(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/addressbook/contact",
        json={"ContactID": "c-001", "FirstName": "Jane"},
        status=200,
    )

    contact = Contact(api_user)
    result = contact.Create(FirstName="Jane", LastName="Doe")

    assert result.Result == "Success"
    assert result.ContactID == "c-001"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body == {"FirstName": "Jane", "LastName": "Doe"}


@responses_lib.activate
def test_create_accepts_a_prebuilt_model(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/addressbook/contact",
        json={"ContactID": "c-002"},
        status=200,
    )

    model = Contact(api_user).Set(FirstName="Bob").Build()
    result = Contact(api_user).Create(model)

    assert result.Result == "Success"


def test_create_rejects_unknown_field_in_dict_model(api_user):
    contact = Contact(api_user)
    result = contact.Create({"Bogus": "x"})

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


@responses_lib.activate
def test_create_dict_model_does_not_inherit_residual_set_state(api_user):
    contact = Contact(api_user)
    contact.Set(Notes="stale note from a prior builder call")

    mock_endpoint(
        responses_lib.POST,
        "/addressbook/contact",
        json={"ContactID": "c-005", "FirstName": "Jane"},
        status=200,
    )

    result = contact.Create({"FirstName": "Jane", "LastName": "Doe"})

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert "Notes" not in sent_body


@responses_lib.activate
def test_update_dispatches_patch_with_escaped_id(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/addressbook/contact/c%2F001",
        json={"ContactID": "c/001", "FirstName": "Jane2"},
        status=200,
    )

    contact = Contact(api_user)
    result = contact.Update("c/001", FirstName="Jane2")

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body == {"FirstName": "Jane2"}


@responses_lib.activate
def test_detail_dispatches_get(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/contact/c-001",
        json={"ContactID": "c-001", "FirstName": "Jane"},
        status=200,
    )

    result = Contact(api_user).Detail("c-001")

    assert result.Result == "Success"
    assert result.FirstName == "Jane"


def test_detail_raises_when_contact_id_is_empty(api_user):
    with pytest.raises(ValueError, match="ContactID"):
        Contact(api_user).Detail("")


@responses_lib.activate
def test_detail_maps_404_to_record_not_found(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/contact/missing",
        json={"ErrorMessage": "not found"},
        status=404,
    )

    result = Contact(api_user).Detail("missing")

    assert result.Result == "RecordNotFound"


@responses_lib.activate
def test_delete_dispatches_delete(api_user):
    mock_endpoint(
        responses_lib.DELETE,
        "/addressbook/contact/c-001",
        json={"ContactID": "c-001"},
        status=200,
    )

    result = Contact(api_user).Delete("c-001")

    assert result.Result == "Success"


@responses_lib.activate
def test_list_dispatches_get_with_paging_query(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/contact/list",
        json={"TotalRecords": 1, "RecordsPerPage": 20, "PageCount": 1, "Page": 1,
              "Contacts": [{"ContactID": "c-001"}]},
        status=200,
    )

    result = Contact(api_user).List(records_per_page=20, page=1)

    assert result.Result == "Success"
    assert result.Contacts[0]["ContactID"] == "c-001"
    query = parse_qs(urlparse(responses_lib.calls[0].request.url).query)
    assert query["recordsPerPage"] == ["20"]
    assert query["page"] == ["1"]


@responses_lib.activate
def test_search_dispatches_get_with_filter_params(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/contact/search",
        json={"TotalRecords": 1, "RecordsPerPage": 20, "PageCount": 1, "Page": 1,
              "Contacts": [{"ContactID": "c-001", "EmailAddress": "jane@example.com"}]},
        status=200,
    )

    result = Contact(api_user).Search(email_address="jane@example.com", first_name="Jane")

    assert result.Result == "Success"
    query = parse_qs(urlparse(responses_lib.calls[0].request.url).query)
    assert query["EmailAddress"] == ["jane@example.com"]
    assert query["FirstName"] == ["Jane"]


@responses_lib.activate
def test_detail_new_pascalcase_kwarg_accepted(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/contact/6000000b-f002-4007-b00a-c00000000001",
        json={"Result": "Success", "ContactID": "6000000b-f002-4007-b00a-c00000000001"},
        status=200,
    )

    contact = Contact(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            contact.Detail(ContactID="6000000b-f002-4007-b00a-c00000000001")
        except TypeError as exc:
            pytest.fail(f"ContactID kwarg not accepted: {exc}")


@responses_lib.activate
def test_detail_old_snake_case_kwarg_still_works_with_warning(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/contact/6000000b-f002-4007-b00a-c00000000001",
        json={"Result": "Success", "ContactID": "6000000b-f002-4007-b00a-c00000000001"},
        status=200,
    )

    contact = Contact(api_user)
    with pytest.warns(DeprecationWarning, match="contact_id"):
        contact.Detail(contact_id="6000000b-f002-4007-b00a-c00000000001")


@responses_lib.activate
def test_list_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/contact/list",
        json={"Result": "Success", "TotalRecords": 0, "Contacts": []},
        status=200,
    )

    contact = Contact(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            contact.List(RecordsPerPage=10, Page=1)
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_search_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/contact/search",
        json={"Result": "Success", "TotalRecords": 0, "Contacts": []},
        status=200,
    )

    contact = Contact(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            contact.Search(FirstName="Joe", RecordsPerPage=10, Page=1)
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_search_old_snake_case_kwargs_still_work_with_warning(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/contact/search",
        json={"Result": "Success", "TotalRecords": 0, "Contacts": []},
        status=200,
    )

    contact = Contact(api_user)
    with pytest.warns(DeprecationWarning):
        contact.Search(first_name="Joe", records_per_page=10, page=1)


def test_old_contact_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="ContactResponseDTO is deprecated"):
        from tnzapi.api.v300.addressbook.models.responses.contact_response import ContactResponseDTO

    from tnzapi.api.v300.addressbook.models.responses.contact_response import ContactResponse
    assert ContactResponseDTO is ContactResponse


def test_old_contact_list_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="ContactListResponseDTO is deprecated"):
        from tnzapi.api.v300.addressbook.models.responses.contact_list_response import ContactListResponseDTO

    from tnzapi.api.v300.addressbook.models.responses.contact_list_response import ContactListResponse
    assert ContactListResponseDTO is ContactListResponse


def test_old_contact_request_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="ContactRequestDTO is deprecated"):
        from tnzapi.api.v300.addressbook.models.requests.contact_request import ContactRequestDTO

    from tnzapi.api.v300.addressbook.models.requests.contact_request import ContactRequest
    assert ContactRequestDTO is ContactRequest


@responses_lib.activate
def test_update_accepts_a_response_instance_projecting_out_readonly_fields(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/addressbook/contact/c-001",
        json={"ContactID": "c-001", "FirstName": "Changed"},
        status=200,
    )

    detail_result = ContactResponse(
        Result="Success",
        ContactID="c-001",
        Owner="admin",
        CreatedTimeLocal="2026-07-01 09:00:00",
        FirstName="Jane",
        LastName="Doe",
    )
    detail_result.FirstName = "Changed"

    result = Contact(api_user).Update("c-001", model=detail_result)

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    # _build_request_body() drops None-valued fields, so only the two
    # explicitly-set ContactRequest fields appear here - every other field
    # on detail_result defaults to None and is filtered out.
    assert sent_body == {"FirstName": "Changed", "LastName": "Doe"}
    assert "ContactID" not in sent_body
    assert "Owner" not in sent_body
    assert "CreatedTimeLocal" not in sent_body
    assert "Result" not in sent_body


@responses_lib.activate
def test_delete_accepts_a_response_instance(api_user):
    mock_endpoint(
        responses_lib.DELETE,
        "/addressbook/contact/c-001",
        json={"ContactID": "c-001"},
        status=200,
    )

    detail_result = ContactResponse(Result="Success", ContactID="c-001", FirstName="Jane")

    result = Contact(api_user).Delete(detail_result)

    assert result.Result == "Success"
    assert responses_lib.calls[0].request.url.endswith("/addressbook/contact/c-001")


@responses_lib.activate
def test_update_id_param_accepts_a_response_instance(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/addressbook/contact/c-001",
        json={"ContactID": "c-001", "FirstName": "Changed"},
        status=200,
    )

    detail_result = ContactResponse(Result="Success", ContactID="c-001", FirstName="Jane")

    result = Contact(api_user).Update(detail_result, FirstName="Changed")

    assert result.Result == "Success"
    assert responses_lib.calls[0].request.url.endswith("/addressbook/contact/c-001")
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body == {"FirstName": "Changed"}
