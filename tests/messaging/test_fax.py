import json
import warnings

import pytest
import responses as responses_lib

from tnzapi.api.v300.messaging.builders.fax import Fax
from tnzapi.core.auth import TNZApiUser
from tnzapi.core.destination import Destination
from tnzapi.core.file_attachment import FileAttachment
from tests.conftest import mock_endpoint


def test_send_message_builds_correct_request_body(api_user):
    fax = Fax(api_user)
    fax.Files = [{"Name": "test.pdf", "Data": "base64data"}]
    fax.Destinations = [{"ToNumber": "+64211234567"}]

    body = fax._build_request_body()

    assert body["Files"] == [{"Name": "test.pdf", "Data": "base64data"}]
    assert body["Destinations"] == [{"ToNumber": "+64211234567"}]


def test_add_destinations_loops_over_items_calling_add_destination(api_user):
    via_singular = Fax(api_user)
    via_singular.AddDestination("+64211234567")
    via_singular.AddDestination("+64211234568")

    via_plural = Fax(api_user)
    result = via_plural.AddDestinations(["+64211234567", "+64211234568"])

    assert result is via_plural
    assert via_plural.Destinations == via_singular.Destinations


def test_add_destinations_accepts_a_tuple(api_user):
    via_singular = Fax(api_user)
    via_singular.AddDestination("+64211234567")
    via_singular.AddDestination("+64211234568")

    via_plural = Fax(api_user)
    result = via_plural.AddDestinations(("+64211234567", "+64211234568"))

    assert result is via_plural
    assert via_plural.Destinations == via_singular.Destinations


def test_add_destinations_rejects_a_bare_string(api_user):
    fax = Fax(api_user)
    with pytest.raises(TypeError):
        fax.AddDestinations("+64211234567")


def test_add_destinations_rejects_a_dict(api_user):
    fax = Fax(api_user)
    with pytest.raises(TypeError):
        fax.AddDestinations({"ToNumber": "+64211234567"})


def test_add_destination_rejects_a_list(api_user):
    fax = Fax(api_user)
    with pytest.raises(TypeError):
        fax.AddDestination(["+64211234567", "+64211234568"])


def test_add_attachments_accepts_a_list_of_bare_paths(api_user, tmp_path):
    path_a = tmp_path / "a.txt"
    path_a.write_text("a")
    path_b = tmp_path / "b.txt"
    path_b.write_text("b")

    via_singular = Fax(api_user)
    via_singular.AddAttachment(str(path_a))
    via_singular.AddAttachment(str(path_b))

    via_plural = Fax(api_user)
    result = via_plural.AddAttachments([str(path_a), str(path_b)])

    assert result is via_plural
    assert via_plural.Files == via_singular.Files


def test_add_attachments_accepts_a_tuple(api_user, tmp_path):
    path_a = tmp_path / "a.txt"
    path_a.write_text("a")
    path_b = tmp_path / "b.txt"
    path_b.write_text("b")

    via_singular = Fax(api_user)
    via_singular.AddAttachment(str(path_a))
    via_singular.AddAttachment(str(path_b))

    via_plural = Fax(api_user)
    result = via_plural.AddAttachments((str(path_a), str(path_b)))

    assert result is via_plural
    assert via_plural.Files == via_singular.Files


def test_add_attachments_rejects_a_bare_string(api_user):
    fax = Fax(api_user)
    with pytest.raises(TypeError):
        fax.AddAttachments("path/to/doc.pdf")


def test_add_attachments_rejects_a_dict(api_user):
    fax = Fax(api_user)
    with pytest.raises(TypeError):
        fax.AddAttachments({"Name": "doc.pdf", "Data": "ZGF0YQ=="})


def test_add_attachments_accepts_a_list_of_file_attachment_instances(api_user):
    via_singular = Fax(api_user)
    via_singular.AddAttachment(FileAttachment(Name="a.pdf", Data="ZGF0YQ=="))
    via_singular.AddAttachment(FileAttachment(Name="b.pdf", Data="ZGF0YQ=="))

    via_plural = Fax(api_user)
    result = via_plural.AddAttachments([
        FileAttachment(Name="a.pdf", Data="ZGF0YQ=="),
        FileAttachment(Name="b.pdf", Data="ZGF0YQ=="),
    ])

    assert result is via_plural
    assert via_plural.Files == via_singular.Files


def test_send_message_rejects_unknown_kwarg(api_user):
    fax = Fax(api_user)
    result = fax.SendMessage(Bogus="x", Files=[{"Name": "a.pdf", "Data": "x"}], Destination="+64211234567")

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


def test_send_message_rejects_missing_destination(api_user):
    fax = Fax(api_user)
    result = fax.SendMessage(Files=[{"Name": "a.pdf", "Data": "x"}])

    assert result.Result == "Failed"
    assert "Destinations" in result.ErrorMessage[0]


def test_send_message_rejects_missing_content(api_user):
    fax = Fax(api_user)
    result = fax.SendMessage(Destination="+64211234567")

    assert result.Result == "Failed"
    assert "Files" in result.ErrorMessage[0]


@responses_lib.activate
def test_send_message_returns_message_id_on_200_with_no_result_field(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/fax",
        json={"MessageID": "msg-001"},
        status=200,
    )

    fax = Fax(api_user)
    result = fax.SendMessage(Files=[{"Name": "a.pdf", "Data": "x"}], Destination="+64211234567")

    assert result.Result == "Success"
    assert result.MessageID == "msg-001"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["Destination"] == "+64211234567"


@responses_lib.activate
def test_send_message_401_maps_to_unauthorized(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/fax",
        json={"ErrorMessage": ["Access denied: Auth Token or credentials are incorrect or have expired."]},
        status=401,
    )

    fax = Fax(api_user)
    result = fax.SendMessage(Files=[{"Name": "a.pdf", "Data": "x"}], Destination="+64211234567")

    assert result.Result == "Unauthorized"


@responses_lib.activate
def test_status_returns_message_detail_with_recipients(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/fax/msg-001",
        json={
            "MessageID": "msg-001",
            "JobStatus": "Completed",
            "Recipients": [
                {"Type": "Fax", "DestSeq": "00000001", "Destination": "+64211234567", "Status": "Success", "Result": "Sent OK"}
            ],
        },
        status=200,
    )

    fax = Fax(api_user)
    result = fax.Status("msg-001")

    assert result.Result == "Success"
    assert result.Recipients[0]["Result"] == "Sent OK"


@responses_lib.activate
def test_status_404_maps_to_record_not_found(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/fax/missing-id",
        json={"ErrorMessage": ["Message not found."]},
        status=404,
    )

    fax = Fax(api_user)
    result = fax.Status("missing-id")

    assert result.Result == "RecordNotFound"


@responses_lib.activate
def test_reschedule_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/fax/msg-001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Delayed", "Action": "Reschedule"},
        status=200,
    )

    fax = Fax(api_user)
    result = fax.Reschedule("msg-001", "2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert result.Action == "Reschedule"


@responses_lib.activate
def test_reschedule_escapes_message_id_in_path(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/fax/msg%2F001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg/001", "Status": "Delayed", "Action": "Reschedule"},
        status=200,
    )

    fax = Fax(api_user)
    result = fax.Reschedule("msg/001", "2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert responses_lib.calls[0].request.url == "https://api.tnz.co.nz/api/v3.00/fax/msg%2F001/reschedule"


@responses_lib.activate
def test_abort_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/fax/msg-001/abort",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Completed", "Action": "Abort"},
        status=200,
    )

    fax = Fax(api_user)
    result = fax.Abort("msg-001")

    assert result.Result == "Success"
    assert result.Action == "Abort"


@responses_lib.activate
def test_resubmit_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/fax/msg-001/resubmit",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Pending", "Action": "Resubmit"},
        status=200,
    )

    fax = Fax(api_user)
    result = fax.Resubmit("msg-001", "2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert result.Action == "Resubmit"


def test_set_applies_multiple_fields_and_returns_self(api_user):
    fax = Fax(api_user)
    returned = fax.Set(Reference="Test", ToNumber="+64211234567")

    assert returned is fax
    assert fax.Reference == "Test"
    assert fax.ToNumber == "+64211234567"


def test_set_raises_on_unknown_field(api_user):
    fax = Fax(api_user)
    with pytest.raises(ValueError):
        fax.Set(Bogus="x")


def test_add_destination_with_string_wraps_as_to_number(api_user):
    fax = Fax(api_user)
    fax.AddDestination("+64211234567")

    assert fax.Destinations == [{"ToNumber": "+64211234567"}]


def test_add_destination_with_dict_appends_as_is(api_user):
    fax = Fax(api_user)
    fax.AddDestination({"ToNumber": "+64211234567", "FirstName": "Alice"})

    assert fax.Destinations == [{"ToNumber": "+64211234567", "FirstName": "Alice"}]


def test_add_destinations_with_mixed_list_adds_each_item(api_user):
    fax = Fax(api_user)
    fax.AddDestinations(["+64211234567", {"ToNumber": "+64221234567", "FirstName": "Bob"}])

    assert fax.Destinations == [{"ToNumber": "+64211234567"}, {"ToNumber": "+64221234567", "FirstName": "Bob"}]


def test_add_destination_with_contact_id(api_user):
    fax = Fax(api_user)
    fax.AddDestination(contact_id="6000000b-f002-4007-b00a-c00000000001")

    assert fax.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_destination_with_group_id(api_user):
    fax = Fax(api_user)
    fax.AddDestination(group_id="4000000b-f002-4007-b00a-c00000000002")

    assert fax.Destinations == [{"GroupID": "4000000b-f002-4007-b00a-c00000000002"}]


def test_add_destination_rejects_unknown_dict_key(api_user):
    fax = Fax(api_user)
    with pytest.raises(ValueError, match="ToNunber"):
        fax.AddDestination({"ToNunber": "+6491234567"})


def test_add_destination_accepts_a_destination_instance(api_user):
    fax = Fax(api_user)
    fax.AddDestination(Destination(ToNumber="+6491234567"))

    assert fax.Destinations == [{"ToNumber": "+6491234567"}]


def test_add_destination_accepts_fax_number(api_user):
    fax = Fax(api_user)
    fax.AddDestination({"FaxNumber": "+6491234567"})

    assert fax.Destinations == [{"FaxNumber": "+6491234567"}]


def test_send_message_rejects_destination_with_unknown_key(api_user):
    fax = Fax(api_user)
    result = fax.SendMessage(
        Files=[{"Name": "doc.pdf", "Data": "base64=="}],
        Destinations=[{"ToNunber": "+6491234567"}],
    )

    assert result.Result == "Failed"
    assert "ToNunber" in result.ErrorMessage[0]


def test_add_destination_chains(api_user):
    fax = Fax(api_user)
    result = fax.AddDestination("+64211234567").AddDestination("+64221234567")

    assert result is fax
    assert len(fax.Destinations) == 2


def test_add_attachment_appends_to_files(api_user):
    fax = Fax(api_user)
    fax.AddAttachment("test.pdf", "base64data")

    assert fax.Files == [{"Name": "test.pdf", "Data": "base64data"}]


def test_add_attachment_accepts_file_attachment_instance(api_user):
    fax = Fax(api_user)
    fax.AddAttachment(FileAttachment(Name="test.pdf", Data="base64data=="))

    assert fax.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_add_attachment_accepts_dict(api_user):
    fax = Fax(api_user)
    fax.AddAttachment({"Name": "test.pdf", "Data": "base64data=="})

    assert fax.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_add_attachment_accepts_single_real_path_string(tmp_path, api_user):
    path = tmp_path / "test.pdf"
    path.write_bytes(b"pdf-bytes")
    fax = Fax(api_user)

    fax.AddAttachment(str(path))

    assert fax.Files[0]["Name"] == "test.pdf"


def test_add_attachment_two_arg_form_with_literal_base64_never_warns(api_user, recwarn):
    fax = Fax(api_user)
    fax.AddAttachment("test.pdf", "base64data==")

    assert fax.Files == [{"Name": "test.pdf", "Data": "base64data=="}]
    assert len(recwarn) == 0


def test_add_attachment_two_arg_form_with_real_path_data_has_no_warning(tmp_path, api_user, recwarn):
    path = tmp_path / "real.pdf"
    path.write_bytes(b"pdf-bytes")
    fax = Fax(api_user)

    fax.AddAttachment("Custom Name.pdf", str(path))

    assert fax.Files[0]["Name"] == "Custom Name.pdf"
    assert len(recwarn) == 0


def test_build_returns_independent_copy(api_user):
    fax = Fax(api_user)
    fax.Reference = "Hi"
    fax.AddDestination("+64211234567")

    model = fax.Build()

    assert model.Reference == "Hi"
    assert model.Destinations == [{"ToNumber": "+64211234567"}]

    # mutating the builder after Build() must not affect the already-returned model
    fax.AddDestination("+64221234567")
    assert len(model.Destinations) == 1
    assert len(fax.Destinations) == 2

    # mutating a destination dict already captured by Build() must not leak through either
    fax.Destinations[0]["ToNumber"] = "+64299999999"
    assert model.Destinations[0]["ToNumber"] == "+64211234567"


def test_builder_chain_then_send_message(api_user):
    fax = Fax(api_user)
    fax.Set(Reference="Builder test").AddDestination("+64211234567").AddDestination(
        {"ToNumber": "+64221234567", "FirstName": "Bob"}
    )

    body = fax._build_request_body()

    assert body["Reference"] == "Builder test"
    assert body["Destinations"] == [{"ToNumber": "+64211234567"}, {"ToNumber": "+64221234567", "FirstName": "Bob"}]


@responses_lib.activate
def test_send_message_accepts_prebuilt_model(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/fax",
        json={"MessageID": "msg-010"},
        status=200,
    )

    builder = Fax(api_user)
    model = (
        builder.Set(Reference="From model")
        .AddDestination("+64211234567")
        .AddAttachment("doc.pdf", "base64data")
        .Build()
    )

    fax = Fax(api_user)
    result = fax.SendMessage(model)

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["Reference"] == "From model"
    assert sent_body["Destinations"] == [{"ToNumber": "+64211234567"}]


@responses_lib.activate
def test_send_message_accepts_prebuilt_dict(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/fax",
        json={"MessageID": "msg-011"},
        status=200,
    )

    fax = Fax(api_user)
    result = fax.SendMessage({
        "Reference": "From dict",
        "Destinations": [{"ToNumber": "+64211234567"}],
        "Files": [{"Name": "a.pdf", "Data": "x"}],
    })

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["Reference"] == "From dict"


def test_send_message_rejects_invalid_model_type(api_user):
    fax = Fax(api_user)
    result = fax.SendMessage(model=12345)

    assert result.Result == "Failed"
    assert "12345" in result.ErrorMessage[0] or "int" in result.ErrorMessage[0]


def test_send_message_rejects_dict_model_with_unknown_key(api_user):
    fax = Fax(api_user)
    result = fax.SendMessage({"Bogus": "x"})

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


@responses_lib.activate
def test_send_message_dict_model_does_not_inherit_residual_set_state(api_user):
    fax = Fax(api_user)
    fax.Set(SubAccount="stale sub account from a prior builder call")

    mock_endpoint(
        responses_lib.POST,
        "/fax",
        json={"MessageID": "msg-013"},
        status=200,
    )

    result = fax.SendMessage({
        "Reference": "Fresh fax",
        "Destinations": [{"ToNumber": "+64211234567"}],
        "Files": [{"Name": "a.pdf", "Data": "x"}],
    })

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert "SubAccount" not in sent_body


@responses_lib.activate
def test_send_message_model_plus_kwargs_kwargs_supplement_model(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/fax",
        json={"MessageID": "msg-012"},
        status=200,
    )

    model = (
        Fax(api_user)
        .Set(Reference="Base")
        .AddDestination("+64211234567")
        .AddAttachment("doc.pdf", "base64data")
        .Build()
    )

    fax = Fax(api_user)
    result = fax.SendMessage(model, ToNumber="+64229999999")

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["Reference"] == "Base"
    assert sent_body["ToNumber"] == "+64229999999"


@responses_lib.activate
def test_send_message_kwargs_only_still_works_unchanged(api_user):
    # Regression guard: the pre-existing kwargs-only call style must be completely unaffected.
    mock_endpoint(
        responses_lib.POST,
        "/fax",
        json={"MessageID": "msg-013"},
        status=200,
    )

    fax = Fax(api_user)
    result = fax.SendMessage(Files=[{"Name": "a.pdf", "Data": "x"}], Destination="+64211234567")

    assert result.Result == "Success"


@responses_lib.activate
def test_status_accepts_new_pascalcase_kwarg(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/fax/msg-001",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    fax = Fax(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            fax.Status(MessageID="msg-001")
        except TypeError as exc:
            pytest.fail(f"MessageID kwarg not accepted: {exc}")


@responses_lib.activate
def test_status_old_snake_case_kwarg_still_works_with_warning(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/fax/msg-001",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    fax = Fax(api_user)
    with pytest.warns(DeprecationWarning, match="message_id"):
        fax.Status(message_id="msg-001")


@responses_lib.activate
def test_reschedule_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/fax/msg-001/reschedule",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    fax = Fax(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            fax.Reschedule(MessageID="msg-001", SendTime="2026-08-01T09:00:00")
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_resubmit_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/fax/msg-001/resubmit",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    fax = Fax(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            fax.Resubmit(MessageID="msg-001", SendTime="2026-08-01T09:00:00")
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


def test_add_destination_new_pascalcase_kwargs_accepted(api_user):
    fax = Fax(api_user)
    fax.AddDestination(ContactID="6000000b-f002-4007-b00a-c00000000001")
    assert fax.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_destination_old_snake_case_kwarg_still_works_with_warning(api_user):
    fax = Fax(api_user)
    with pytest.warns(DeprecationWarning, match="contact_id"):
        fax.AddDestination(contact_id="6000000b-f002-4007-b00a-c00000000001")
    assert fax.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_attachment_new_pascalcase_kwargs_accepted(api_user):
    fax = Fax(api_user)
    fax.AddAttachment(Name="test.pdf", Data="base64data==")
    assert fax.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_old_fax_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="FaxResponseDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.fax_response import FaxResponseDTO

    from tnzapi.api.v300.messaging.models.responses.fax_response import FaxResponse
    assert FaxResponseDTO is FaxResponse


def test_old_fax_status_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="FaxStatusDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.fax_status import FaxStatusDTO

    from tnzapi.api.v300.messaging.models.responses.fax_status import FaxStatus
    assert FaxStatusDTO is FaxStatus


def test_old_fax_action_result_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="FaxActionResultDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.fax_action_result import FaxActionResultDTO

    from tnzapi.api.v300.messaging.models.responses.fax_action_result import FaxActionResult
    assert FaxActionResultDTO is FaxActionResult


def test_old_fax_request_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="FaxRequestDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.requests.fax_request import FaxRequestDTO

    from tnzapi.api.v300.messaging.models.requests.fax_request import FaxRequest
    assert FaxRequestDTO is FaxRequest
