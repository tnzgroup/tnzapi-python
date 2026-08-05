import json
import warnings

import pytest
import responses as responses_lib

from tnzapi.api.v300.messaging.builders.rcs import RCS
from tnzapi.core.auth import TNZApiUser
from tnzapi.core.destination import Destination
from tnzapi.core.file_attachment import FileAttachment
from tests.conftest import mock_endpoint


def test_add_destinations_loops_over_items_calling_add_destination(api_user):
    via_singular = RCS(api_user)
    via_singular.AddDestination("+64211111111")
    via_singular.AddDestination("+64211111112")

    via_plural = RCS(api_user)
    result = via_plural.AddDestinations(["+64211111111", "+64211111112"])

    assert result is via_plural
    assert via_plural.Destinations == via_singular.Destinations


def test_add_destinations_accepts_a_tuple(api_user):
    via_singular = RCS(api_user)
    via_singular.AddDestination("+64211111111")
    via_singular.AddDestination("+64211111112")

    via_plural = RCS(api_user)
    result = via_plural.AddDestinations(("+64211111111", "+64211111112"))

    assert result is via_plural
    assert via_plural.Destinations == via_singular.Destinations


def test_add_destinations_rejects_a_bare_string(api_user):
    rcs = RCS(api_user)
    with pytest.raises(TypeError):
        rcs.AddDestinations("+64211111111")


def test_add_destinations_rejects_a_dict(api_user):
    rcs = RCS(api_user)
    with pytest.raises(TypeError):
        rcs.AddDestinations({"ToNumber": "+64211111111"})


def test_add_destination_rejects_a_list(api_user):
    rcs = RCS(api_user)
    with pytest.raises(TypeError):
        rcs.AddDestination(["+64211111111", "+64211111112"])


def test_add_attachments_accepts_a_list_of_bare_paths(api_user, tmp_path):
    path_a = tmp_path / "a.txt"
    path_a.write_text("a")
    path_b = tmp_path / "b.txt"
    path_b.write_text("b")

    via_singular = RCS(api_user)
    via_singular.AddAttachment(str(path_a))
    via_singular.AddAttachment(str(path_b))

    via_plural = RCS(api_user)
    result = via_plural.AddAttachments([str(path_a), str(path_b)])

    assert result is via_plural
    assert via_plural.Files == via_singular.Files


def test_add_attachments_accepts_a_tuple(api_user, tmp_path):
    path_a = tmp_path / "a.txt"
    path_a.write_text("a")
    path_b = tmp_path / "b.txt"
    path_b.write_text("b")

    via_singular = RCS(api_user)
    via_singular.AddAttachment(str(path_a))
    via_singular.AddAttachment(str(path_b))

    via_plural = RCS(api_user)
    result = via_plural.AddAttachments((str(path_a), str(path_b)))

    assert result is via_plural
    assert via_plural.Files == via_singular.Files


def test_add_attachments_rejects_a_bare_string(api_user):
    rcs = RCS(api_user)
    with pytest.raises(TypeError):
        rcs.AddAttachments("path/to/doc.pdf")


def test_add_attachments_rejects_a_dict(api_user):
    rcs = RCS(api_user)
    with pytest.raises(TypeError):
        rcs.AddAttachments({"Name": "doc.pdf", "Data": "ZGF0YQ=="})


def test_add_attachments_accepts_a_list_of_file_attachment_instances(api_user):
    via_singular = RCS(api_user)
    via_singular.AddAttachment(FileAttachment(Name="a.pdf", Data="ZGF0YQ=="))
    via_singular.AddAttachment(FileAttachment(Name="b.pdf", Data="ZGF0YQ=="))

    via_plural = RCS(api_user)
    result = via_plural.AddAttachments([
        FileAttachment(Name="a.pdf", Data="ZGF0YQ=="),
        FileAttachment(Name="b.pdf", Data="ZGF0YQ=="),
    ])

    assert result is via_plural
    assert via_plural.Files == via_singular.Files


def test_fallback_mode_accepts_a_list_and_joins_it(api_user):
    rcs = RCS(api_user)
    rcs.Message = "hi"
    rcs.Destinations = [{"ToNumber": "+64211111111"}]
    rcs.Set(FallbackMode=["Voice", "WhatsApp"])

    assert rcs._build_request_body()["FallbackMode"] == "Voice, WAPP"


def test_fallback_mode_single_string_still_works_unchanged(api_user):
    rcs = RCS(api_user)
    rcs.Message = "hi"
    rcs.Destinations = [{"ToNumber": "+64211111111"}]
    rcs.Set(FallbackMode="SMS")

    assert rcs._build_request_body()["FallbackMode"] == "SMS"


def test_send_message_builds_correct_request_body(api_user):
    rcs = RCS(api_user)
    rcs.Message = "Hello world"
    rcs.Destinations = [{"ToNumber": "+64211234567"}]

    body = rcs._build_request_body()

    assert body["Message"] == "Hello world"
    # CharacterConversion defaults to False, which _build_request_body's filter drops (matching
    # every other bool-defaulting field) - set explicitly below to prove it round-trips when set.


def test_send_message_includes_character_conversion_when_set(api_user):
    # RCS shares SMS's CTL-building pipeline server-side (SMSCTLBuilder, reused with
    # DEST_MODE=RCS) - CharacterConversion is a real, functional field for RCS too, not just
    # SMS, despite being absent from the OpenAPI spec's RCS `properties:` schema (it does
    # appear in that endpoint's own "Display all parameters" example, which is correct).
    rcs = RCS(api_user)
    rcs.Message = "Hello world"
    rcs.Destinations = [{"ToNumber": "+64211234567"}]
    rcs.CharacterConversion = True

    body = rcs._build_request_body()

    assert body["CharacterConversion"] is True


def test_send_message_rejects_unknown_kwarg(api_user):
    rcs = RCS(api_user)
    result = rcs.SendMessage(Bogus="x", Message="hi", Destination="+64211234567")

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


def test_send_message_rejects_missing_destination(api_user):
    rcs = RCS(api_user)
    result = rcs.SendMessage(Message="hi")

    assert result.Result == "Failed"
    assert "Destinations" in result.ErrorMessage[0]


def test_send_message_rejects_missing_message(api_user):
    rcs = RCS(api_user)
    result = rcs.SendMessage(Destination="+64211234567")

    assert result.Result == "Failed"
    assert "Message" in result.ErrorMessage[0]


def test_received_rejects_time_period_out_of_range(api_user):
    rcs = RCS(api_user)

    result = rcs.Received(TimePeriod=0)

    assert result.Result == "Failed"
    assert "TimePeriod" in result.ErrorMessage[0]


@responses_lib.activate
def test_send_message_returns_message_id_on_200_with_no_result_field(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/rcs",
        json={"MessageID": "msg-001"},
        status=200,
    )

    rcs = RCS(api_user)
    result = rcs.SendMessage(Message="Hi", Destination="+64211234567")

    assert result.Result == "Success"
    assert result.MessageID == "msg-001"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["Message"] == "Hi"


@responses_lib.activate
def test_send_message_401_maps_to_unauthorized(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/rcs",
        json={"ErrorMessage": ["Access denied: Auth Token or credentials are incorrect or have expired."]},
        status=401,
    )

    rcs = RCS(api_user)
    result = rcs.SendMessage(Message="Hi", Destination="+64211234567")

    assert result.Result == "Unauthorized"


@responses_lib.activate
def test_status_returns_message_detail_with_recipients(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/rcs/msg-001",
        json={
            "MessageID": "msg-001",
            "JobStatus": "Completed",
            "Recipients": [
                {"Type": "RCS", "DestSeq": "00000001", "Destination": "+64211234567", "Status": "Success", "SMSReplies": []}
            ],
        },
        status=200,
    )

    rcs = RCS(api_user)
    result = rcs.Status("msg-001")

    assert result.Result == "Success"
    assert result.Recipients[0]["SMSReplies"] == []


@responses_lib.activate
def test_status_omits_404_ref(api_user):
    # Per spec, RCS Status errors list only 400/401/500 (no explicit 404), unlike other channels -
    # confirm a generic 400 still maps correctly rather than assuming a 404 code path is reachable.
    mock_endpoint(
        responses_lib.GET,
        "/rcs/bad-id",
        json={"ErrorMessage": ["Invalid MessageID format."]},
        status=400,
    )

    rcs = RCS(api_user)
    result = rcs.Status("bad-id")

    assert result.Result == "Failed"


@responses_lib.activate
def test_reschedule_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/rcs/msg-001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Delayed", "Action": "Reschedule"},
        status=200,
    )

    rcs = RCS(api_user)
    result = rcs.Reschedule("msg-001", "2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert result.Action == "Reschedule"


@responses_lib.activate
def test_abort_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/rcs/msg-001/abort",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Completed", "Action": "Abort"},
        status=200,
    )

    rcs = RCS(api_user)
    result = rcs.Abort("msg-001")

    assert result.Result == "Success"
    assert result.Action == "Abort"


@responses_lib.activate
def test_received_returns_messages(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/rcs/received",
        json={
            "TotalRecords": 1,
            "RecordsPerPage": 20,
            "PageCount": 1,
            "Page": 1,
            "Messages": [{"ReceivedID": "a1b2c3d4-e5f6-7890-1234-567890abcdee", "From": "+6421000001", "MessageText": "Hi there"}],
        },
        status=200,
    )

    rcs = RCS(api_user)
    result = rcs.Received(time_period=10)

    assert result.Result == "Success"
    assert result.Messages[0]["MessageText"] == "Hi there"


def test_set_applies_multiple_fields_and_returns_self(api_user):
    rcs = RCS(api_user)
    returned = rcs.Set(Message="Hi", Reference="Test")

    assert returned is rcs
    assert rcs.Message == "Hi"
    assert rcs.Reference == "Test"


def test_set_raises_on_unknown_field(api_user):
    rcs = RCS(api_user)
    with pytest.raises(ValueError):
        rcs.Set(Bogus="x")


def test_add_destination_with_string_wraps_as_to_number(api_user):
    rcs = RCS(api_user)
    rcs.AddDestination("+64211234567")

    assert rcs.Destinations == [{"ToNumber": "+64211234567"}]


def test_add_destination_with_dict_appends_as_is(api_user):
    rcs = RCS(api_user)
    rcs.AddDestination({"ToNumber": "+64211234567", "FirstName": "Alice"})

    assert rcs.Destinations == [{"ToNumber": "+64211234567", "FirstName": "Alice"}]


def test_add_destinations_with_mixed_list_adds_each_item(api_user):
    rcs = RCS(api_user)
    rcs.AddDestinations(["+64211234567", {"ToNumber": "+64221234567", "FirstName": "Bob"}])

    assert rcs.Destinations == [{"ToNumber": "+64211234567"}, {"ToNumber": "+64221234567", "FirstName": "Bob"}]


def test_add_destination_with_contact_id(api_user):
    rcs = RCS(api_user)
    rcs.AddDestination(contact_id="6000000b-f002-4007-b00a-c00000000001")

    assert rcs.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_destination_with_group_id(api_user):
    rcs = RCS(api_user)
    rcs.AddDestination(group_id="4000000b-f002-4007-b00a-c00000000002")

    assert rcs.Destinations == [{"GroupID": "4000000b-f002-4007-b00a-c00000000002"}]


def test_add_destination_rejects_unknown_dict_key(api_user):
    rcs = RCS(api_user)
    with pytest.raises(ValueError, match="ToNunber"):
        rcs.AddDestination({"ToNunber": "+64211234567"})


def test_add_destination_accepts_a_destination_instance(api_user):
    rcs = RCS(api_user)
    rcs.AddDestination(Destination(ToNumber="+64211234567", FirstName="Alice"))

    assert rcs.Destinations == [{"ToNumber": "+64211234567", "FirstName": "Alice"}]


def test_add_destination_accepts_mobile_phone(api_user):
    rcs = RCS(api_user)
    rcs.AddDestination({"MobilePhone": "+64211234567"})

    assert rcs.Destinations == [{"MobilePhone": "+64211234567"}]


def test_send_message_rejects_destination_with_unknown_key(api_user):
    rcs = RCS(api_user)
    result = rcs.SendMessage(Message="Hi", Destinations=[{"ToNunber": "+64211234567"}])

    assert result.Result == "Failed"
    assert "ToNunber" in result.ErrorMessage[0]


def test_add_destination_chains(api_user):
    rcs = RCS(api_user)
    result = rcs.AddDestination("+64211234567").AddDestination("+64221234567")

    assert result is rcs
    assert len(rcs.Destinations) == 2


def test_add_attachment_appends_to_files(api_user):
    rcs = RCS(api_user)
    rcs.AddAttachment("test.pdf", "base64data==")

    assert rcs.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_add_attachment_accepts_file_attachment_instance(api_user):
    rcs = RCS(api_user)
    rcs.AddAttachment(FileAttachment(Name="test.pdf", Data="base64data=="))

    assert rcs.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_add_attachment_accepts_dict(api_user):
    rcs = RCS(api_user)
    rcs.AddAttachment({"Name": "test.pdf", "Data": "base64data=="})

    assert rcs.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_add_attachment_accepts_single_real_path_string(tmp_path, api_user):
    path = tmp_path / "test.pdf"
    path.write_bytes(b"pdf-bytes")
    rcs = RCS(api_user)

    rcs.AddAttachment(str(path))

    assert rcs.Files[0]["Name"] == "test.pdf"


def test_add_attachment_two_arg_form_with_literal_base64_never_warns(api_user, recwarn):
    rcs = RCS(api_user)
    rcs.AddAttachment("test.pdf", "base64data==")

    assert rcs.Files == [{"Name": "test.pdf", "Data": "base64data=="}]
    assert len(recwarn) == 0


def test_add_attachment_two_arg_form_with_real_path_data_has_no_warning(tmp_path, api_user, recwarn):
    path = tmp_path / "real.pdf"
    path.write_bytes(b"pdf-bytes")
    rcs = RCS(api_user)

    rcs.AddAttachment("Custom Name.pdf", str(path))

    assert rcs.Files[0]["Name"] == "Custom Name.pdf"
    assert len(recwarn) == 0


def test_build_returns_independent_copy(api_user):
    rcs = RCS(api_user)
    rcs.Message = "Hi"
    rcs.AddDestination("+64211234567")

    model = rcs.Build()

    assert model.Message == "Hi"
    assert model.Destinations == [{"ToNumber": "+64211234567"}]

    # mutating the builder after Build() must not affect the already-returned model
    rcs.AddDestination("+64221234567")
    assert len(model.Destinations) == 1
    assert len(rcs.Destinations) == 2

    # mutating a destination dict already captured by Build() must not leak through either
    rcs.Destinations[0]["ToNumber"] = "+64299999999"
    assert model.Destinations[0]["ToNumber"] == "+64211234567"


@responses_lib.activate
def test_send_message_accepts_prebuilt_model(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/rcs",
        json={"MessageID": "msg-010"},
        status=200,
    )

    builder = RCS(api_user)
    model = builder.Set(Message="From model").AddDestination("+64211234567").Build()

    rcs = RCS(api_user)
    result = rcs.SendMessage(model)

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["Message"] == "From model"
    assert sent_body["Destinations"] == [{"ToNumber": "+64211234567"}]


@responses_lib.activate
def test_send_message_accepts_prebuilt_dict(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/rcs",
        json={"MessageID": "msg-011"},
        status=200,
    )

    rcs = RCS(api_user)
    result = rcs.SendMessage({"Message": "From dict", "Destinations": [{"ToNumber": "+64211234567"}]})

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["Message"] == "From dict"


def test_send_message_rejects_invalid_model_type(api_user):
    rcs = RCS(api_user)
    result = rcs.SendMessage(model=12345)

    assert result.Result == "Failed"
    assert "12345" in result.ErrorMessage[0] or "int" in result.ErrorMessage[0]


def test_send_message_rejects_dict_model_with_unknown_key(api_user):
    rcs = RCS(api_user)
    result = rcs.SendMessage({"Bogus": "x"})

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


@responses_lib.activate
def test_send_message_dict_model_does_not_inherit_residual_set_state(api_user):
    rcs = RCS(api_user)
    rcs.Set(Reference="stale reference from a prior builder call")

    mock_endpoint(
        responses_lib.POST,
        "/rcs",
        json={"MessageID": "msg-013"},
        status=200,
    )

    result = rcs.SendMessage({"Message": "Fresh message", "Destinations": [{"ToNumber": "+64211234567"}]})

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert "Reference" not in sent_body


@responses_lib.activate
def test_send_message_kwargs_only_still_works_unchanged(api_user):
    # Regression guard: the pre-existing kwargs-only call style must be completely unaffected.
    mock_endpoint(
        responses_lib.POST,
        "/rcs",
        json={"MessageID": "msg-013"},
        status=200,
    )

    rcs = RCS(api_user)
    result = rcs.SendMessage(Message="Old style", Destination="+64211234567")

    assert result.Result == "Success"


@responses_lib.activate
def test_status_accepts_new_pascalcase_kwarg(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/rcs/msg-001",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    rcs = RCS(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            rcs.Status(MessageID="msg-001")
        except TypeError as exc:
            pytest.fail(f"MessageID kwarg not accepted: {exc}")


@responses_lib.activate
def test_status_old_snake_case_kwarg_still_works_with_warning(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/rcs/msg-001",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    rcs = RCS(api_user)
    with pytest.warns(DeprecationWarning, match="message_id"):
        rcs.Status(message_id="msg-001")


@responses_lib.activate
def test_received_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/rcs/received",
        json={"Result": "Success", "TotalRecords": 0, "Messages": []},
        status=200,
    )

    rcs = RCS(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            rcs.Received(TimePeriod=10, RecordsPerPage=5, Page=2)
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


def test_add_destination_new_pascalcase_kwargs_accepted(api_user):
    rcs = RCS(api_user)
    rcs.AddDestination(ContactID="6000000b-f002-4007-b00a-c00000000001")
    assert rcs.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_destination_old_snake_case_kwarg_still_works_with_warning(api_user):
    rcs = RCS(api_user)
    with pytest.warns(DeprecationWarning, match="contact_id"):
        rcs.AddDestination(contact_id="6000000b-f002-4007-b00a-c00000000001")
    assert rcs.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_attachment_new_pascalcase_kwargs_accepted(api_user):
    rcs = RCS(api_user)
    rcs.AddAttachment(Name="test.pdf", Data="base64data==")
    assert rcs.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_old_rcs_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="RCSResponseDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.rcs_response import RCSResponseDTO

    from tnzapi.api.v300.messaging.models.responses.rcs_response import RCSResponse
    assert RCSResponseDTO is RCSResponse


def test_old_rcs_status_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="RCSStatusDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.rcs_status import RCSStatusDTO

    from tnzapi.api.v300.messaging.models.responses.rcs_status import RCSStatus
    assert RCSStatusDTO is RCSStatus


def test_old_rcs_action_result_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="RCSActionResultDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.rcs_action_result import RCSActionResultDTO

    from tnzapi.api.v300.messaging.models.responses.rcs_action_result import RCSActionResult
    assert RCSActionResultDTO is RCSActionResult


def test_old_rcs_received_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="RCSReceivedDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.rcs_received import RCSReceivedDTO

    from tnzapi.api.v300.messaging.models.responses.rcs_received import RCSReceived
    assert RCSReceivedDTO is RCSReceived


def test_old_rcs_request_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="RCSRequestDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.requests.rcs_request import RCSRequestDTO

    from tnzapi.api.v300.messaging.models.requests.rcs_request import RCSRequest
    assert RCSRequestDTO is RCSRequest
