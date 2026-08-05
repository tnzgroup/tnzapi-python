import json
import warnings

import pytest
import responses as responses_lib

from tnzapi.api.v300.addressbook.builders.group import Group
from tnzapi.api.v300.addressbook.models.requests.group_request import GroupRequest
from tnzapi.api.v300.addressbook.models.responses.group_response import GroupResponse
from tests.conftest import mock_endpoint


def test_set_raises_on_unknown_field(api_user):
    group = Group(api_user)

    with pytest.raises(ValueError):
        group.Set(Bogus="x")


def test_build_returns_independent_copy(api_user):
    group = Group(api_user)
    group.Set(GroupName="VIP")

    model = group.Build()

    assert isinstance(model, GroupRequest)
    assert model.GroupName == "VIP"

    group.Set(GroupName="Changed")
    assert model.GroupName == "VIP"


@responses_lib.activate
def test_create_dispatches_post(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/addressbook/group",
        json={"GroupID": "g-001", "GroupName": "VIP"},
        status=200,
    )

    result = Group(api_user).Create(GroupName="VIP")

    assert result.Result == "Success"
    assert result.GroupID == "g-001"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body == {"GroupName": "VIP"}


def test_create_rejects_unknown_field_in_dict_model(api_user):
    result = Group(api_user).Create({"Bogus": "x"})

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


@responses_lib.activate
def test_create_dict_model_does_not_inherit_residual_set_state(api_user):
    group = Group(api_user)
    group.Set(SubAccount="stale sub account from a prior builder call")

    mock_endpoint(
        responses_lib.POST,
        "/addressbook/group",
        json={"GroupID": "g-002", "GroupName": "VIP"},
        status=200,
    )

    result = group.Create({"GroupName": "VIP"})

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert "SubAccount" not in sent_body


@responses_lib.activate
def test_update_dispatches_patch_with_escaped_id(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/addressbook/group/g%2F001",
        json={"GroupID": "g/001", "GroupName": "VIP2"},
        status=200,
    )

    result = Group(api_user).Update("g/001", GroupName="VIP2")

    assert result.Result == "Success"


@responses_lib.activate
def test_detail_dispatches_get(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/group/g-001",
        json={"GroupID": "g-001", "GroupName": "VIP"},
        status=200,
    )

    result = Group(api_user).Detail("g-001")

    assert result.Result == "Success"
    assert result.GroupName == "VIP"


def test_detail_raises_when_group_id_is_empty(api_user):
    with pytest.raises(ValueError, match="GroupID"):
        Group(api_user).Detail("")


@responses_lib.activate
def test_delete_dispatches_delete(api_user):
    mock_endpoint(
        responses_lib.DELETE,
        "/addressbook/group/g-001",
        json={"GroupID": "g-001"},
        status=200,
    )

    result = Group(api_user).Delete("g-001")

    assert result.Result == "Success"


@responses_lib.activate
def test_list_dispatches_get_with_paging_query(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/group/list",
        json={"TotalRecords": 1, "RecordsPerPage": 20, "PageCount": 1, "Page": 1,
              "Groups": [{"GroupID": "g-001"}]},
        status=200,
    )

    result = Group(api_user).List()

    assert result.Result == "Success"
    assert result.Groups[0]["GroupID"] == "g-001"


@responses_lib.activate
def test_detail_maps_401_to_unauthorized(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/group/g-001",
        json={"ErrorMessage": "bad token"},
        status=401,
    )

    result = Group(api_user).Detail("g-001")

    assert result.Result == "Unauthorized"


@responses_lib.activate
def test_detail_new_pascalcase_kwarg_accepted(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/group/4000000b-f002-4007-b00a-c00000000002",
        json={"Result": "Success", "GroupID": "4000000b-f002-4007-b00a-c00000000002"},
        status=200,
    )

    group = Group(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            group.Detail(GroupID="4000000b-f002-4007-b00a-c00000000002")
        except TypeError as exc:
            pytest.fail(f"GroupID kwarg not accepted: {exc}")


@responses_lib.activate
def test_detail_old_snake_case_kwarg_still_works_with_warning(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/group/4000000b-f002-4007-b00a-c00000000002",
        json={"Result": "Success", "GroupID": "4000000b-f002-4007-b00a-c00000000002"},
        status=200,
    )

    group = Group(api_user)
    with pytest.warns(DeprecationWarning, match="group_id"):
        group.Detail(group_id="4000000b-f002-4007-b00a-c00000000002")


@responses_lib.activate
def test_list_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/addressbook/group/list",
        json={"Result": "Success", "TotalRecords": 0, "Groups": []},
        status=200,
    )

    group = Group(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            group.List(RecordsPerPage=10, Page=1)
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


def test_old_group_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="GroupResponseDTO is deprecated"):
        from tnzapi.api.v300.addressbook.models.responses.group_response import GroupResponseDTO

    from tnzapi.api.v300.addressbook.models.responses.group_response import GroupResponse
    assert GroupResponseDTO is GroupResponse


def test_old_group_list_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="GroupListResponseDTO is deprecated"):
        from tnzapi.api.v300.addressbook.models.responses.group_list_response import GroupListResponseDTO

    from tnzapi.api.v300.addressbook.models.responses.group_list_response import GroupListResponse
    assert GroupListResponseDTO is GroupListResponse


def test_old_group_request_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="GroupRequestDTO is deprecated"):
        from tnzapi.api.v300.addressbook.models.requests.group_request import GroupRequestDTO

    from tnzapi.api.v300.addressbook.models.requests.group_request import GroupRequest
    assert GroupRequestDTO is GroupRequest


@responses_lib.activate
def test_update_accepts_a_response_instance_projecting_out_readonly_fields(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/addressbook/group/g-001",
        json={"GroupID": "g-001", "GroupName": "Changed"},
        status=200,
    )

    detail_result = GroupResponse(
        Result="Success",
        GroupID="g-001",
        Owner="admin",
        CreatedTimeLocal="2026-07-01 09:00:00",
        GroupName="VIP",
        SubAccount="sub-1",
    )
    detail_result.GroupName = "Changed"

    result = Group(api_user).Update("g-001", model=detail_result)

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body == {"GroupName": "Changed", "SubAccount": "sub-1"}
    assert "GroupID" not in sent_body
    assert "Owner" not in sent_body
    assert "CreatedTimeLocal" not in sent_body


@responses_lib.activate
def test_delete_accepts_a_response_instance(api_user):
    mock_endpoint(
        responses_lib.DELETE,
        "/addressbook/group/g-001",
        json={"GroupID": "g-001"},
        status=200,
    )

    detail_result = GroupResponse(Result="Success", GroupID="g-001", GroupName="VIP")

    result = Group(api_user).Delete(detail_result)

    assert result.Result == "Success"
    assert responses_lib.calls[0].request.url.endswith("/addressbook/group/g-001")


@responses_lib.activate
def test_update_id_param_accepts_a_response_instance(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/addressbook/group/g-001",
        json={"GroupID": "g-001", "GroupName": "Changed"},
        status=200,
    )

    detail_result = GroupResponse(Result="Success", GroupID="g-001", GroupName="VIP")

    result = Group(api_user).Update(detail_result, GroupName="Changed")

    assert result.Result == "Success"
    assert responses_lib.calls[0].request.url.endswith("/addressbook/group/g-001")
