import json
import warnings
from urllib.parse import parse_qs, urlparse

import pytest
import responses as responses_lib

from tnzapi.api.v300.optout.builders.optout import OptOut
from tnzapi.api.v300.optout.models.requests.optout_request import OptOutRequest
from tnzapi.api.v300.optout.models.responses.optout_response import OptOutResponse
from tests.conftest import mock_endpoint


def test_getattr_raises_attribute_error_instead_of_recursing_when_data_unset(api_user):
    # An instance constructed without __init__ running (e.g. copy/pickle/
    # object.__new__) has no `_data` yet - __getattr__ must not recurse into
    # itself trying to resolve `_data`.
    obj = OptOut.__new__(OptOut)

    with pytest.raises(AttributeError):
        obj.DestType


def test_set_applies_known_fields(api_user):
    optout = OptOut(api_user)
    optout.Set(DestType="SMS", Destination="+64211234567")

    assert optout.DestType == "SMS"
    assert optout.Destination == "+64211234567"


def test_set_raises_on_unknown_field(api_user):
    optout = OptOut(api_user)

    with pytest.raises(ValueError):
        optout.Set(Bogus="x")


def test_build_returns_independent_copy(api_user):
    optout = OptOut(api_user)
    optout.Set(DestType="SMS", Destination="+64211234567")

    model = optout.Build()

    assert isinstance(model, OptOutRequest)
    assert model.Destination == "+64211234567"

    optout.Set(Destination="+64299999999")
    assert model.Destination == "+64211234567"


@responses_lib.activate
def test_create_dispatches_post_with_valid_fields(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/optout",
        json={"ID": "o-001", "DestType": "SMS", "Destination": "+64211234567"},
        status=200,
    )

    result = OptOut(api_user).Create(DestType="SMS", Destination="+64211234567")

    assert result.Result == "Success"
    assert result.ID == "o-001"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body == {"DestType": "SMS", "Destination": "+64211234567"}


def test_create_rejects_missing_dest_type(api_user):
    result = OptOut(api_user).Create(Destination="+64211234567")

    assert result.Result == "Failed"
    assert "DestType" in result.ErrorMessage[0]


def test_create_rejects_unsupported_dest_type(api_user):
    result = OptOut(api_user).Create(DestType="WhatsApp", Destination="+64211234567")

    assert result.Result == "Failed"
    assert "DestType" in result.ErrorMessage[0]


@responses_lib.activate
def test_create_accepts_sms_alias_for_text(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/optout",
        json={"ID": "o-002", "DestType": "SMS"},
        status=200,
    )

    result = OptOut(api_user).Create(DestType="SMS", Destination="+64211234567")

    assert result.Result == "Success"


@responses_lib.activate
def test_create_accepts_voice_alias_for_speech(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/optout",
        json={"ID": "o-003", "DestType": "Voice"},
        status=200,
    )

    result = OptOut(api_user).Create(DestType="Voice", Destination="+64211234567")

    assert result.Result == "Success"


def test_create_requires_destination_or_contact_id(api_user):
    result = OptOut(api_user).Create(DestType="SMS")

    assert result.Result == "Failed"
    assert "Destination" in result.ErrorMessage[0] or "ContactID" in result.ErrorMessage[0]


@responses_lib.activate
def test_create_accepts_contact_id_without_destination(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/optout",
        json={"ID": "o-004", "DestType": "Email", "ContactID": "c-001"},
        status=200,
    )

    result = OptOut(api_user).Create(DestType="Email", ContactID="c-001")

    assert result.Result == "Success"


@responses_lib.activate
def test_create_dict_model_does_not_inherit_residual_set_state(api_user):
    optout = OptOut(api_user)
    optout.Set(Notes="stale note from a prior builder call")

    mock_endpoint(
        responses_lib.POST,
        "/optout",
        json={"ID": "o-007", "DestType": "SMS"},
        status=200,
    )

    result = optout.Create({"DestType": "SMS", "Destination": "+64211234567"})

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert "Notes" not in sent_body


@responses_lib.activate
def test_update_dispatches_patch_with_escaped_id(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/optout/o%2F001",
        json={"ID": "o/001", "Notes": "updated"},
        status=200,
    )

    result = OptOut(api_user).Update("o/001", Notes="updated")

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body == {"Notes": "updated"}


@responses_lib.activate
def test_update_allows_partial_fields_without_dest_type(api_user):
    # Update() is a partial PATCH - it must not require DestType/Destination/ContactID
    # the way Create() does, since a caller might only be touching Notes.
    mock_endpoint(
        responses_lib.PATCH,
        "/optout/o-001",
        json={"ID": "o-001", "Notes": "just a note change"},
        status=200,
    )

    result = OptOut(api_user).Update("o-001", Notes="just a note change")

    assert result.Result == "Success"


def test_update_still_validates_dest_type_if_supplied(api_user):
    result = OptOut(api_user).Update("o-001", DestType="WhatsApp")

    assert result.Result == "Failed"
    assert "DestType" in result.ErrorMessage[0]


@responses_lib.activate
def test_update_dict_model_does_not_inherit_residual_set_state(api_user):
    optout = OptOut(api_user)
    optout.Set(DestType="SMS", Destination="+64211234567")

    mock_endpoint(
        responses_lib.PATCH,
        "/optout/o-001",
        json={"ID": "o-001", "Notes": "just a note change"},
        status=200,
    )

    result = optout.Update("o-001", {"Notes": "just a note change"})

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body == {"Notes": "just a note change"}


@responses_lib.activate
def test_details_dispatches_get(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/optout/o-001",
        json={"ID": "o-001", "DestType": "SMS"},
        status=200,
    )

    result = OptOut(api_user).Details("o-001")

    assert result.Result == "Success"
    assert result.DestType == "SMS"


def test_details_raises_when_opt_out_id_is_empty(api_user):
    with pytest.raises(ValueError, match="OptOutID"):
        OptOut(api_user).Details("")


@responses_lib.activate
def test_details_maps_404_to_record_not_found(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/optout/missing",
        json={"ErrorMessage": "not found"},
        status=404,
    )

    result = OptOut(api_user).Details("missing")

    assert result.Result == "RecordNotFound"


@responses_lib.activate
def test_delete_dispatches_delete(api_user):
    mock_endpoint(
        responses_lib.DELETE,
        "/optout/o-001",
        json={"ID": "o-001"},
        status=200,
    )

    result = OptOut(api_user).Delete("o-001")

    assert result.Result == "Success"


@responses_lib.activate
def test_list_dispatches_get_with_default_paging(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/optout/list",
        json={"TotalRecords": 1, "RecordsPerPage": 100, "PageCount": 1, "Page": 1,
              "OptOuts": [{"ID": "o-001", "DestType": "SMS"}]},
        status=200,
    )

    result = OptOut(api_user).List()

    assert result.Result == "Success"
    assert result.OptOuts[0]["ID"] == "o-001"
    query = parse_qs(urlparse(responses_lib.calls[0].request.url).query)
    assert query["recordsPerPage"] == ["100"]
    assert query["page"] == ["1"]


@responses_lib.activate
def test_list_dispatches_get_with_all_filters(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/optout/list",
        json={"TotalRecords": 0, "RecordsPerPage": 20, "PageCount": 0, "Page": 1, "OptOuts": []},
        status=200,
    )

    result = OptOut(api_user).List(time_period=5, dest_type="SMS", contact_id="c-001", page=2, records_per_page=20)

    assert result.Result == "Success"
    query = parse_qs(urlparse(responses_lib.calls[0].request.url).query)
    assert query["timePeriod"] == ["5"]
    assert query["destType"] == ["SMS"]
    assert query["contactID"] == ["c-001"]
    assert query["page"] == ["2"]
    assert query["recordsPerPage"] == ["20"]


@responses_lib.activate
def test_create_batch_dispatches_post_with_multiple_dest_types(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/optout/batch",
        json={"ID": "o-005", "DestType": "SMS,Voice"},
        status=200,
    )

    result = OptOut(api_user).CreateBatch(dest_type="SMS,Voice", destinations=["+64211111111", "+64222222222"])

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body == {"DestType": "SMS,Voice", "Destinations": ["+64211111111", "+64222222222"]}


@responses_lib.activate
def test_create_batch_normalizes_whitespace_around_comma_delimited_dest_types(api_user):
    # Validation tolerates "SMS, Voice" (with a space), but the value actually
    # sent to the API must not carry that whitespace through.
    mock_endpoint(
        responses_lib.POST,
        "/optout/batch",
        json={"ID": "o-008", "DestType": "SMS,Voice"},
        status=200,
    )

    result = OptOut(api_user).CreateBatch(dest_type="SMS, Voice", destinations=["+64211111111"])

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["DestType"] == "SMS,Voice"


def test_create_batch_rejects_unsupported_dest_type_in_comma_list(api_user):
    result = OptOut(api_user).CreateBatch(dest_type="SMS,WhatsApp", destinations=["+64211111111"])

    assert result.Result == "Failed"
    assert "DestType" in result.ErrorMessage[0]


def test_create_batch_requires_a_destination_or_contact_field(api_user):
    result = OptOut(api_user).CreateBatch(dest_type="SMS")

    assert result.Result == "Failed"


@responses_lib.activate
def test_create_batch_accepts_contact_ids_without_destinations(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/optout/batch",
        json={"ID": "o-006", "DestType": "Email"},
        status=200,
    )

    result = OptOut(api_user).CreateBatch(dest_type="Email", contact_ids=["c-001", "c-002"])

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body == {"DestType": "Email", "ContactIDs": ["c-001", "c-002"]}

@responses_lib.activate
def test_details_new_pascalcase_kwarg_accepted(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/optout/00000000-0000-0000-0000-000000000000",
        json={"Result": "Success", "ID": "00000000-0000-0000-0000-000000000000"},
        status=200,
    )

    optout = OptOut(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            optout.Details(OptOutID="00000000-0000-0000-0000-000000000000")
        except TypeError as exc:
            pytest.fail(f"OptOutID kwarg not accepted: {exc}")


@responses_lib.activate
def test_details_old_snake_case_kwarg_still_works_with_warning(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/optout/00000000-0000-0000-0000-000000000000",
        json={"Result": "Success", "ID": "00000000-0000-0000-0000-000000000000"},
        status=200,
    )

    optout = OptOut(api_user)
    with pytest.warns(DeprecationWarning, match="opt_out_id"):
        optout.Details(opt_out_id="00000000-0000-0000-0000-000000000000")


@responses_lib.activate
def test_list_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/optout/list",
        json={"Result": "Success", "TotalRecords": 0, "OptOuts": []},
        status=200,
    )

    optout = OptOut(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            optout.List(DestType="SMS", RecordsPerPage=20, Page=1)
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_create_batch_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/optout/batch",
        json={"Result": "Success"},
        status=200,
    )

    optout = OptOut(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            optout.CreateBatch(DestType="SMS", Destinations=["+64211234567"])
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_create_batch_old_snake_case_kwargs_still_work_with_warning(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/optout/batch",
        json={"Result": "Success"},
        status=200,
    )

    optout = OptOut(api_user)
    with pytest.warns(DeprecationWarning):
        optout.CreateBatch(dest_type="SMS", destinations=["+64211234567"])


def test_old_optout_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="OptOutResponseDTO is deprecated"):
        from tnzapi.api.v300.optout.models.responses.optout_response import OptOutResponseDTO

    from tnzapi.api.v300.optout.models.responses.optout_response import OptOutResponse
    assert OptOutResponseDTO is OptOutResponse


def test_old_optout_list_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="OptOutListResponseDTO is deprecated"):
        from tnzapi.api.v300.optout.models.responses.optout_list_response import OptOutListResponseDTO

    from tnzapi.api.v300.optout.models.responses.optout_list_response import OptOutListResponse
    assert OptOutListResponseDTO is OptOutListResponse


def test_old_optout_request_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="OptOutRequestDTO is deprecated"):
        from tnzapi.api.v300.optout.models.requests.optout_request import OptOutRequestDTO

    from tnzapi.api.v300.optout.models.requests.optout_request import OptOutRequest
    assert OptOutRequestDTO is OptOutRequest


def test_old_optout_batch_request_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="OptOutBatchRequestDTO is deprecated"):
        from tnzapi.api.v300.optout.models.requests.optout_batch_request import OptOutBatchRequestDTO

    from tnzapi.api.v300.optout.models.requests.optout_batch_request import OptOutBatchRequest
    assert OptOutBatchRequestDTO is OptOutBatchRequest


@responses_lib.activate
def test_update_accepts_a_response_instance_projecting_out_readonly_fields(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/optout/o-001",
        json={"ID": "o-001", "Notes": "Changed"},
        status=200,
    )

    details_result = OptOutResponse(
        Result="Success",
        ID="o-001",
        DestType="SMS",
        Destination="+64211234567",
        CreatedTimeLocal="2026-07-01 09:00:00",
        Notes="original note",
    )
    details_result.Notes = "Changed"

    result = OptOut(api_user).Update("o-001", model=details_result)

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body == {"DestType": "SMS", "Destination": "+64211234567", "Notes": "Changed"}
    assert "ID" not in sent_body
    assert "CreatedTimeLocal" not in sent_body
    assert "Result" not in sent_body


@responses_lib.activate
def test_delete_accepts_a_response_instance(api_user):
    mock_endpoint(
        responses_lib.DELETE,
        "/optout/o-001",
        json={"ID": "o-001"},
        status=200,
    )

    details_result = OptOutResponse(Result="Success", ID="o-001", DestType="SMS")

    result = OptOut(api_user).Delete(details_result)

    assert result.Result == "Success"
    assert responses_lib.calls[0].request.url.endswith("/optout/o-001")


@responses_lib.activate
def test_update_id_param_accepts_a_response_instance(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/optout/o-001",
        json={"ID": "o-001", "Notes": "Changed"},
        status=200,
    )

    details_result = OptOutResponse(Result="Success", ID="o-001", DestType="SMS", Destination="+64211234567")

    result = OptOut(api_user).Update(details_result, Notes="Changed")

    assert result.Result == "Success"
    assert responses_lib.calls[0].request.url.endswith("/optout/o-001")
