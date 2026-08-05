import json
import warnings
from urllib.parse import parse_qs, urlparse

import pytest
import responses as responses_lib

from tnzapi.api.v300.addressbook.builders.contact_group import ContactGroup
from tests.conftest import mock_endpoint


@responses_lib.activate
def test_create_dispatches_patch_to_contact_side(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/addressbook/contact/c-001/group",
        json={"Contact": {"ContactID": "c-001"}, "Group": {"GroupID": "g-001"}},
        status=200,
    )

    result = ContactGroup(api_user).Create("c-001", "g-001")

    assert result.Result == "Success"
    assert result.Contact["ContactID"] == "c-001"
    assert result.Group["GroupID"] == "g-001"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body == {"GroupID": "g-001"}


@responses_lib.activate
def test_delete_dispatches_delete_with_escaped_ids(api_user):
    mock_endpoint(
        responses_lib.DELETE,
        "/addressbook/contact/c%2F001/group/g-001",
        json={"Contact": {"ContactID": "c/001"}, "Group": {"GroupID": "g-001"}},
        status=200,
    )

    result = ContactGroup(api_user).Delete("c/001", "g-001")

    assert result.Result == "Success"


@responses_lib.activate
def test_list_dispatches_get_with_paging_query(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/contact/c-001/group/list",
        json={"TotalRecords": 1, "RecordsPerPage": 20, "PageCount": 1, "Page": 1,
              "Contact": {"ContactID": "c-001"}, "Groups": [{"GroupID": "g-001"}]},
        status=200,
    )

    result = ContactGroup(api_user).List("c-001")

    assert result.Result == "Success"
    assert result.Groups[0]["GroupID"] == "g-001"


@responses_lib.activate
def test_detail_finds_matching_group_via_list(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/contact/c-001/group/list",
        json={"TotalRecords": 2, "RecordsPerPage": 100, "PageCount": 1, "Page": 1,
              "Contact": {"ContactID": "c-001"},
              "Groups": [{"GroupID": "g-001"}, {"GroupID": "g-002"}]},
        status=200,
    )

    result = ContactGroup(api_user).Detail("c-001", "g-002")

    assert result.Result == "Success"
    assert result.Group["GroupID"] == "g-002"


@responses_lib.activate
def test_detail_returns_record_not_found_when_group_absent(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/contact/c-001/group/list",
        json={"TotalRecords": 1, "RecordsPerPage": 100, "PageCount": 1, "Page": 1,
              "Contact": {"ContactID": "c-001"}, "Groups": [{"GroupID": "g-001"}]},
        status=200,
    )

    result = ContactGroup(api_user).Detail("c-001", "g-999")

    assert result.Result == "RecordNotFound"


@responses_lib.activate
def test_detail_accepts_an_explicit_page_instead_of_walking_all_pages(api_user):
    # Detail() only scans the requested page rather than silently walking every
    # page on the caller's behalf - the caller decides how far to look by passing
    # page/records_per_page explicitly, based on List()'s own PageCount.
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/contact/c-001/group/list",
        json={"TotalRecords": 150, "RecordsPerPage": 100, "PageCount": 2, "Page": 2,
              "Contact": {"ContactID": "c-001"}, "Groups": [{"GroupID": "g-150"}]},
        status=200,
    )

    result = ContactGroup(api_user).Detail("c-001", "g-150", page=2)

    assert result.Result == "Success"
    assert result.Group["GroupID"] == "g-150"
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

    cg = ContactGroup(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            cg.Create(ContactID="c1", GroupID="g1")
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

    cg = ContactGroup(api_user)
    with pytest.warns(DeprecationWarning):
        cg.Create(contact_id="c1", group_id="g1")


@responses_lib.activate
def test_list_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/contact/c1/group/list",
        json={"Result": "Success", "TotalRecords": 0, "Groups": []},
        status=200,
    )

    cg = ContactGroup(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            cg.List(ContactID="c1", RecordsPerPage=10, Page=1)
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


def test_old_contact_group_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="ContactGroupResponseDTO is deprecated"):
        from tnzapi.api.v300.addressbook.models.responses.contact_group_response import ContactGroupResponseDTO

    from tnzapi.api.v300.addressbook.models.responses.contact_group_response import ContactGroupResponse
    assert ContactGroupResponseDTO is ContactGroupResponse


def test_old_contact_group_list_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="ContactGroupListResponseDTO is deprecated"):
        from tnzapi.api.v300.addressbook.models.responses.contact_group_list_response import ContactGroupListResponseDTO

    from tnzapi.api.v300.addressbook.models.responses.contact_group_list_response import ContactGroupListResponse
    assert ContactGroupListResponseDTO is ContactGroupListResponse


def test_create_raises_when_contact_id_is_empty(api_user):
    with pytest.raises(ValueError, match="ContactID"):
        ContactGroup(api_user).Create("", "g-001")


def test_create_raises_when_group_id_is_none(api_user):
    with pytest.raises(ValueError, match="GroupID"):
        ContactGroup(api_user).Create("c-001", None)


def test_delete_raises_when_contact_id_is_empty(api_user):
    with pytest.raises(ValueError, match="ContactID"):
        ContactGroup(api_user).Delete("", "g-001")


def test_list_raises_when_contact_id_is_empty(api_user):
    with pytest.raises(ValueError, match="ContactID"):
        ContactGroup(api_user).List("")


def test_detail_raises_when_group_id_is_empty(api_user):
    with pytest.raises(ValueError, match="GroupID"):
        ContactGroup(api_user).Detail("c-001", "")
