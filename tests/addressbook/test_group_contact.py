import json
import warnings
from urllib.parse import parse_qs, urlparse

import pytest
import responses as responses_lib

from tnzapi.api.v300.addressbook.builders.group_contact import GroupContact
from tests.conftest import mock_endpoint


@responses_lib.activate
def test_create_wraps_the_contact_side_endpoint(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/addressbook/contact/c-001/group",
        json={"Contact": {"ContactID": "c-001"}, "Group": {"GroupID": "g-001"}},
        status=200,
    )

    result = GroupContact(api_user).Create("g-001", "c-001")

    assert result.Result == "Success"
    assert result.Group["GroupID"] == "g-001"
    assert result.Contact["ContactID"] == "c-001"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body == {"GroupID": "g-001"}


@responses_lib.activate
def test_delete_wraps_the_contact_side_endpoint(api_user):
    mock_endpoint(
        responses_lib.DELETE,
        "/addressbook/contact/c-001/group/g-001",
        json={"Contact": {"ContactID": "c-001"}, "Group": {"GroupID": "g-001"}},
        status=200,
    )

    result = GroupContact(api_user).Delete("g-001", "c-001")

    assert result.Result == "Success"


@responses_lib.activate
def test_list_dispatches_get_with_escaped_group_id(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/group/g%2F001/contact/list",
        json={"TotalRecords": 1, "RecordsPerPage": 20, "PageCount": 1, "Page": 1,
              "Group": {"GroupID": "g/001"}, "Contacts": [{"ContactID": "c-001"}]},
        status=200,
    )

    result = GroupContact(api_user).List("g/001")

    assert result.Result == "Success"
    assert result.Contacts[0]["ContactID"] == "c-001"


@responses_lib.activate
def test_detail_finds_matching_contact_via_list(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/group/g-001/contact/list",
        json={"TotalRecords": 2, "RecordsPerPage": 100, "PageCount": 1, "Page": 1,
              "Group": {"GroupID": "g-001"},
              "Contacts": [{"ContactID": "c-001"}, {"ContactID": "c-002"}]},
        status=200,
    )

    result = GroupContact(api_user).Detail("g-001", "c-002")

    assert result.Result == "Success"
    assert result.Contact["ContactID"] == "c-002"


@responses_lib.activate
def test_detail_returns_record_not_found_when_contact_absent(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/group/g-001/contact/list",
        json={"TotalRecords": 1, "RecordsPerPage": 100, "PageCount": 1, "Page": 1,
              "Group": {"GroupID": "g-001"}, "Contacts": [{"ContactID": "c-001"}]},
        status=200,
    )

    result = GroupContact(api_user).Detail("g-001", "c-999")

    assert result.Result == "RecordNotFound"


@responses_lib.activate
def test_detail_accepts_an_explicit_page_instead_of_walking_all_pages(api_user):
    # Detail() only scans the requested page rather than silently walking every
    # page on the caller's behalf - the caller decides how far to look by passing
    # page/records_per_page explicitly, based on List()'s own PageCount.
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/group/g-001/contact/list",
        json={"TotalRecords": 150, "RecordsPerPage": 100, "PageCount": 2, "Page": 2,
              "Group": {"GroupID": "g-001"}, "Contacts": [{"ContactID": "c-150"}]},
        status=200,
    )

    result = GroupContact(api_user).Detail("g-001", "c-150", page=2)

    assert result.Result == "Success"
    assert result.Contact["ContactID"] == "c-150"
    query = parse_qs(urlparse(responses_lib.calls[0].request.url).query)
    assert query["page"] == ["2"]


@responses_lib.activate
def test_create_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/addressbook/contact/c1/group",
        json={"Result": "Success"},
        status=200,
    )

    gc = GroupContact(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            gc.Create(GroupID="g1", ContactID="c1")
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_create_old_snake_case_kwargs_still_work_with_warning(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/addressbook/contact/c1/group",
        json={"Result": "Success"},
        status=200,
    )

    gc = GroupContact(api_user)
    with pytest.warns(DeprecationWarning):
        gc.Create(group_id="g1", contact_id="c1")


@responses_lib.activate
def test_list_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/group/g1/contact/list",
        json={"Result": "Success", "TotalRecords": 0, "Contacts": []},
        status=200,
    )

    gc = GroupContact(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            gc.List(GroupID="g1", RecordsPerPage=10, Page=1)
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


def test_old_group_contact_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="GroupContactResponseDTO is deprecated"):
        from tnzapi.api.v300.addressbook.models.responses.group_contact_response import GroupContactResponseDTO

    from tnzapi.api.v300.addressbook.models.responses.group_contact_response import GroupContactResponse
    assert GroupContactResponseDTO is GroupContactResponse


def test_old_group_contact_list_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="GroupContactListResponseDTO is deprecated"):
        from tnzapi.api.v300.addressbook.models.responses.group_contact_list_response import GroupContactListResponseDTO

    from tnzapi.api.v300.addressbook.models.responses.group_contact_list_response import GroupContactListResponse
    assert GroupContactListResponseDTO is GroupContactListResponse


def test_create_raises_when_group_id_is_empty(api_user):
    with pytest.raises(ValueError, match="GroupID"):
        GroupContact(api_user).Create("", "c-001")


def test_create_raises_when_contact_id_is_none(api_user):
    with pytest.raises(ValueError, match="ContactID"):
        GroupContact(api_user).Create("g-001", None)


def test_delete_raises_when_group_id_is_empty(api_user):
    with pytest.raises(ValueError, match="GroupID"):
        GroupContact(api_user).Delete("", "c-001")


def test_list_raises_when_group_id_is_empty(api_user):
    with pytest.raises(ValueError, match="GroupID"):
        GroupContact(api_user).List("")


def test_detail_raises_when_contact_id_is_empty(api_user):
    with pytest.raises(ValueError, match="ContactID"):
        GroupContact(api_user).Detail("g-001", "")
