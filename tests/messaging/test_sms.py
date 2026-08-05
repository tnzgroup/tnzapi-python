import json
import warnings

import pytest
import responses as responses_lib

from tnzapi.api.v300.messaging.builders.sms import SMS
from tnzapi.core.destination import Destination
from tnzapi.core.file_attachment import FileAttachment
from tests.conftest import mock_endpoint


def test_send_message_builds_correct_request_body(api_user):
    sms = SMS(api_user)
    sms.Message = "Hello world"
    sms.Destinations = [{"ToNumber": "+64211234567"}]

    body = sms._build_request_body()

    assert body["Message"] == "Hello world"
    assert body["Destinations"] == [{"ToNumber": "+64211234567"}]
    assert "ChargeCode" not in body  # dropped in v3.00


def test_add_destinations_loops_over_items_calling_add_destination(api_user):
    via_singular = SMS(api_user)
    via_singular.AddDestination("+64211234567")
    via_singular.AddDestination("+64211234568")

    via_plural = SMS(api_user)
    result = via_plural.AddDestinations(["+64211234567", "+64211234568"])

    assert result is via_plural
    assert via_plural.Destinations == via_singular.Destinations


def test_add_destinations_accepts_a_tuple(api_user):
    via_singular = SMS(api_user)
    via_singular.AddDestination("+64211234567")
    via_singular.AddDestination("+64211234568")

    via_plural = SMS(api_user)
    result = via_plural.AddDestinations(("+64211234567", "+64211234568"))

    assert result is via_plural
    assert via_plural.Destinations == via_singular.Destinations


def test_add_destinations_rejects_a_bare_string(api_user):
    sms = SMS(api_user)
    with pytest.raises(TypeError):
        sms.AddDestinations("+64211234567")


def test_add_destinations_rejects_a_dict(api_user):
    # A dict iterates over its keys, silently adding one garbage destination
    # per key rather than the intended single destination.
    sms = SMS(api_user)
    with pytest.raises(TypeError):
        sms.AddDestinations({"ToNumber": "+64211234567"})


def test_add_destination_rejects_a_list(api_user):
    sms = SMS(api_user)
    with pytest.raises(TypeError):
        sms.AddDestination(["+64211234567", "+64211234568"])


def test_add_attachments_accepts_a_list_of_bare_paths(api_user, tmp_path):
    path_a = tmp_path / "a.txt"
    path_a.write_text("a")
    path_b = tmp_path / "b.txt"
    path_b.write_text("b")

    via_singular = SMS(api_user)
    via_singular.AddAttachment(str(path_a))
    via_singular.AddAttachment(str(path_b))

    via_plural = SMS(api_user)
    result = via_plural.AddAttachments([str(path_a), str(path_b)])

    assert result is via_plural
    assert via_plural.Files == via_singular.Files


def test_add_attachments_accepts_a_tuple(api_user, tmp_path):
    path_a = tmp_path / "a.txt"
    path_a.write_text("a")
    path_b = tmp_path / "b.txt"
    path_b.write_text("b")

    via_singular = SMS(api_user)
    via_singular.AddAttachment(str(path_a))
    via_singular.AddAttachment(str(path_b))

    via_plural = SMS(api_user)
    result = via_plural.AddAttachments((str(path_a), str(path_b)))

    assert result is via_plural
    assert via_plural.Files == via_singular.Files


def test_add_attachments_rejects_a_bare_string(api_user):
    sms = SMS(api_user)
    with pytest.raises(TypeError):
        sms.AddAttachments("path/to/doc.pdf")


def test_add_attachments_rejects_a_dict(api_user):
    sms = SMS(api_user)
    with pytest.raises(TypeError):
        sms.AddAttachments({"Name": "doc.pdf", "Data": "ZGF0YQ=="})


def test_add_attachments_accepts_a_list_of_file_attachment_instances(api_user):
    via_singular = SMS(api_user)
    via_singular.AddAttachment(FileAttachment(Name="a.pdf", Data="ZGF0YQ=="))
    via_singular.AddAttachment(FileAttachment(Name="b.pdf", Data="ZGF0YQ=="))

    via_plural = SMS(api_user)
    result = via_plural.AddAttachments([
        FileAttachment(Name="a.pdf", Data="ZGF0YQ=="),
        FileAttachment(Name="b.pdf", Data="ZGF0YQ=="),
    ])

    assert result is via_plural
    assert via_plural.Files == via_singular.Files


def test_fallback_mode_accepts_a_list_and_joins_it(api_user):
    sms = SMS(api_user)
    sms.Message = "hi"
    sms.Destinations = [{"ToNumber": "+64211234567"}]
    sms.Set(FallbackMode=["Voice", "WhatsApp"])

    assert sms._build_request_body()["FallbackMode"] == "Voice, WAPP"


def test_fallback_mode_single_string_still_works_unchanged(api_user):
    sms = SMS(api_user)
    sms.Message = "hi"
    sms.Destinations = [{"ToNumber": "+64211234567"}]
    sms.Set(FallbackMode="SMS")

    assert sms._build_request_body()["FallbackMode"] == "SMS"


def test_mode_accepts_send_mode_enum_identically_to_plain_string(api_user):
    from tnzapi.core.send_mode import SendMode

    via_enum = SMS(api_user)
    via_enum.Message = "Hello world"
    via_enum.Destinations = [{"ToNumber": "+64211234567"}]
    via_enum.Mode = SendMode.Test

    via_string = SMS(api_user)
    via_string.Message = "Hello world"
    via_string.Destinations = [{"ToNumber": "+64211234567"}]
    via_string.Mode = "Test"

    body_via_enum = via_enum._build_request_body()
    body_via_string = via_string._build_request_body()

    assert body_via_enum == body_via_string
    assert body_via_enum["Mode"] == "Test"
    assert json.dumps(body_via_enum) == json.dumps(body_via_string)


def test_send_message_to_number_field_round_trips(api_user):
    sms = SMS(api_user)
    sms.Message = "Hello world"
    sms.ToNumber = "+64211234567"

    body = sms._build_request_body()

    assert body["ToNumber"] == "+64211234567"
    assert body["Message"] == "Hello world"


def test_set_destinations_converts_a_bare_string_using_to_number(api_user):
    sms = SMS(api_user)

    sms.Set(Destinations=["+64211234567"])

    assert sms.Destinations == [{"ToNumber": "+64211234567"}]


def test_set_and_add_destination_produce_identical_output_for_the_same_string(api_user):
    via_set = SMS(api_user)
    via_set.Set(Destinations=["+64211234567"])

    via_add_destination = SMS(api_user)
    via_add_destination.AddDestination("+64211234567")

    assert via_set.Destinations == via_add_destination.Destinations


@responses_lib.activate
def test_send_message_returns_message_id_on_200_with_no_result_field(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/sms",
        json={"MessageID": "msg-001"},
        status=200,
    )

    sms = SMS(api_user)
    result = sms.SendMessage(Message="Hi", Destinations=[{"ToNumber": "+64211234567"}])

    assert result.Result == "Success"
    assert result.MessageID == "msg-001"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["Message"] == "Hi"
    assert sent_body["Destinations"] == [{"ToNumber": "+64211234567"}]


def test_send_message_rejects_unknown_kwarg(api_user):
    sms = SMS(api_user)
    result = sms.SendMessage(Bogus="x", Message="hi", Destinations=[{"ToNumber": "+64211234567"}])

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


def test_send_message_rejects_missing_destination(api_user):
    sms = SMS(api_user)
    result = sms.SendMessage(Message="hi")

    assert result.Result == "Failed"
    assert "Destinations" in result.ErrorMessage[0]


def test_send_message_rejects_missing_message(api_user):
    sms = SMS(api_user)
    result = sms.SendMessage(Destinations=[{"ToNumber": "+64211234567"}])

    assert result.Result == "Failed"
    assert "Message" in result.ErrorMessage[0]


@responses_lib.activate
def test_send_message_accepts_template_id_alone_as_content(api_user):
    # docs/sms.md documents "Either Message or TemplateID must be provided" -
    # a regression guard for a real bug where the content-required check only
    # looked at Message, wrongly rejecting a TemplateID-only send.
    mock_endpoint(responses_lib.POST, "/sms", json={"MessageID": "msg-001"}, status=200)

    sms = SMS(api_user)
    result = sms.SendMessage(TemplateID="tpl-001", Destinations=[{"ToNumber": "+64211234567"}])

    assert result.Result == "Success"


@responses_lib.activate
def test_send_message_accepts_contact_id_alone_as_destination(api_user):
    # docs/sms.md documents ContactID as a standalone alternative to Destinations -
    # a regression guard for a real bug where the destination-required check only
    # looked at Destinations/Destination/ToNumber, wrongly rejecting this.
    mock_endpoint(responses_lib.POST, "/sms", json={"MessageID": "msg-001"}, status=200)

    sms = SMS(api_user)
    result = sms.SendMessage(Message="hi", ContactID="c-001")

    assert result.Result == "Success"


@responses_lib.activate
def test_send_message_accepts_group_id_alone_as_destination(api_user):
    mock_endpoint(responses_lib.POST, "/sms", json={"MessageID": "msg-001"}, status=200)

    sms = SMS(api_user)
    result = sms.SendMessage(Message="hi", GroupID="g-001")

    assert result.Result == "Success"


@responses_lib.activate
def test_send_message_401_maps_to_unauthorized(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/sms",
        json={"ErrorMessage": ["Access denied: Auth Token or credentials are incorrect or have expired."]},
        status=401,
    )

    sms = SMS(api_user)
    result = sms.SendMessage(Message="Hi", Destinations=[{"ToNumber": "+64211234567"}])

    assert result.Result == "Unauthorized"
    assert result.ErrorMessage == ["Access denied: Auth Token or credentials are incorrect or have expired."]


@responses_lib.activate
def test_status_returns_message_detail_with_recipients(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/sms/msg-001",
        json={
            "MessageID": "msg-001",
            "JobStatus": "Completed",
            "JobNum": "10AB20CE",
            "Count": 1,
            "Complete": 1,
            "Success": 1,
            "Failed": 0,
            "TotalRecords": 1,
            "RecordsPerPage": 20,
            "PageCount": 1,
            "Page": 1,
            "Recipients": [
                {
                    "Type": "SMS",
                    "DestSeq": "00000001",
                    "Destination": "+64211234567",
                    "Status": "Success",
                    "Result": "Delivered",
                    "SMSReplies": [],
                }
            ],
        },
        status=200,
    )

    sms = SMS(api_user)
    result = sms.Status("msg-001")

    assert result.Result == "Success"
    assert result.MessageID == "msg-001"
    assert result.JobStatus == "Completed"
    assert result.Recipients[0]["Destination"] == "+64211234567"
    assert result.Recipients[0]["SMSReplies"] == []


def test_status_recipients_are_typed_sms_recipient_dto_instances(api_user):
    from tnzapi.api.v300.messaging.models.responses.sms_recipient import SMSRecipient
    from tnzapi.api.v300.messaging.models.responses.sms_status import SMSStatus

    dto = SMSStatus(Recipients=[{"Destination": "+64211234567", "SMSReplies": []}])

    assert isinstance(dto.Recipients[0], SMSRecipient)
    assert dto.Recipients[0].Destination == "+64211234567"


def test_status_recipients_none_does_not_crash():
    from tnzapi.api.v300.messaging.models.responses.sms_status import SMSStatus

    dto = SMSStatus(Recipients=None)

    assert dto.Recipients is None


def test_status_nested_smsreplies_are_typed_sms_reply_dto_instances():
    from tnzapi.api.v300.messaging.models.responses.sms_reply import SMSReply
    from tnzapi.api.v300.messaging.models.responses.sms_status import SMSStatus

    dto = SMSStatus(Recipients=[
        {"Destination": "+64211234567", "SMSReplies": [{"MessageText": "STOP"}]}
    ])

    assert isinstance(dto.Recipients[0].SMSReplies[0], SMSReply)
    assert dto.Recipients[0].SMSReplies[0].MessageText == "STOP"


def test_status_asdict_never_leaks_extras_even_with_unknown_api_fields():
    import dataclasses
    import json

    from tnzapi.api.v300.messaging.models.responses.sms_status import SMSStatus

    dto = SMSStatus(Result="Success", Recipients=[
        {"Destination": "+64211234567", "SomeNewField": "x", "SMSReplies": [{"MessageText": "STOP", "AnotherNewField": "y"}]}
    ])

    serialized = json.dumps(dataclasses.asdict(dto))

    assert "_extras" not in serialized
    assert "SomeNewField" not in serialized
    assert "AnotherNewField" not in serialized


def test_status_to_dict_round_trips_unknown_api_fields_asdict_does_not():
    from tnzapi.api.v300.messaging.models.responses.sms_status import SMSStatus

    dto = SMSStatus(Result="Success", Recipients=[
        {"Destination": "+64211234567", "SomeNewField": "x", "SMSReplies": [{"MessageText": "STOP"}]}
    ])

    assert dto.to_dict()["Recipients"][0]["SomeNewField"] == "x"


@responses_lib.activate
def test_reply_delegates_to_status_and_returns_typed_recipients(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/sms/msg-001",
        json={
            "MessageID": "msg-001",
            "JobStatus": "Completed",
            "Recipients": [
                {
                    "Destination": "+64211234567",
                    "SMSReplies": [{"MessageText": "STOP", "From": "+64211234567"}],
                }
            ],
        },
        status=200,
    )

    sms = SMS(api_user)
    result = sms.Reply("msg-001")

    assert result.Result == "Success"
    assert result.Recipients[0].Destination == "+64211234567"
    assert result.Recipients[0].SMSReplies[0].MessageText == "STOP"
    # Dict-style access still works on the same typed objects
    assert result.Recipients[0]["Destination"] == "+64211234567"


@responses_lib.activate
def test_status_404_maps_to_record_not_found(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/sms/missing-id",
        json={"ErrorMessage": ["Message not found."]},
        status=404,
    )

    sms = SMS(api_user)
    result = sms.Status("missing-id")

    assert result.Result == "RecordNotFound"
    assert result.ErrorMessage == ["Message not found."]


def test_status_raises_when_message_id_is_empty(api_user):
    sms = SMS(api_user)

    with pytest.raises(ValueError, match="MessageID"):
        sms.Status("")


@responses_lib.activate
def test_reschedule_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/sms/msg-001/reschedule",
        json={
            "ActionResult": "Success",
            "MessageID": "msg-001",
            "JobNum": "10AB20CE",
            "Status": "Delayed",
            "Action": "Reschedule",
        },
        status=200,
    )

    sms = SMS(api_user)
    result = sms.Reschedule("msg-001", "2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert result.ActionResult == "Success"
    assert result.Action == "Reschedule"
    assert json.loads(responses_lib.calls[0].request.body) == {"SendTime": "2026-08-01T09:00:00"}


@responses_lib.activate
def test_reschedule_404_maps_to_record_not_found(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/sms/missing-id/reschedule",
        json={"ErrorMessage": ["Message not found."]},
        status=404,
    )

    sms = SMS(api_user)
    result = sms.Reschedule("missing-id", "2026-08-01T09:00:00")

    assert result.Result == "RecordNotFound"


@responses_lib.activate
def test_reschedule_escapes_message_id_in_path(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/sms/msg%2F001/reschedule",
        json={
            "ActionResult": "Success",
            "MessageID": "msg/001",
            "Status": "Delayed",
            "Action": "Reschedule",
        },
        status=200,
    )

    sms = SMS(api_user)
    result = sms.Reschedule("msg/001", "2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert responses_lib.calls[0].request.url == "https://api.tnz.co.nz/api/v3.00/sms/msg%2F001/reschedule"


def test_reschedule_raises_when_message_id_is_none(api_user):
    sms = SMS(api_user)

    with pytest.raises(ValueError, match="MessageID"):
        sms.Reschedule(None, "2026-08-01T09:00:00")


@responses_lib.activate
def test_abort_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/sms/msg-001/abort",
        json={
            "ActionResult": "Success",
            "MessageID": "msg-001",
            "JobNum": "10AB20CE",
            "Status": "Completed",
            "Action": "Abort",
        },
        status=200,
    )

    sms = SMS(api_user)
    result = sms.Abort("msg-001")

    assert result.Result == "Success"
    assert result.ActionResult == "Success"
    assert result.Action == "Abort"


@responses_lib.activate
def test_abort_404_maps_to_record_not_found(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/sms/missing-id/abort",
        json={"ErrorMessage": ["Message not found."]},
        status=404,
    )

    sms = SMS(api_user)
    result = sms.Abort("missing-id")

    assert result.Result == "RecordNotFound"


def test_abort_raises_when_message_id_is_empty(api_user):
    sms = SMS(api_user)

    with pytest.raises(ValueError, match="MessageID"):
        sms.Abort("")


def test_received_rejects_time_period_out_of_range(api_user):
    sms = SMS(api_user)

    result = sms.Received(TimePeriod=1441)

    assert result.Result == "Failed"
    assert "TimePeriod" in result.ErrorMessage[0]


@responses_lib.activate
def test_received_returns_messages(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/sms/received",
        json={
            "TotalRecords": 1,
            "RecordsPerPage": 20,
            "PageCount": 1,
            "Page": 1,
            "Messages": [
                {
                    "ReceivedID": "a1b2c3d4-e5f6-7890-1234-567890abcdee",
                    "From": "+6421000001",
                    "MessageText": "Hi there",
                }
            ],
        },
        status=200,
    )

    sms = SMS(api_user)
    result = sms.Received(time_period=10)

    assert result.Result == "Success"
    assert result.Messages[0]["MessageText"] == "Hi there"


def test_set_applies_multiple_fields_and_returns_self(api_user):
    sms = SMS(api_user)
    returned = sms.Set(Message="Hi", Reference="Test")

    assert returned is sms
    assert sms.Message == "Hi"
    assert sms.Reference == "Test"


def test_set_raises_on_unknown_field(api_user):
    sms = SMS(api_user)
    with pytest.raises(ValueError):
        sms.Set(Bogus="x")


def test_add_destination_with_string_wraps_as_to_number(api_user):
    sms = SMS(api_user)
    sms.AddDestination("+64211234567")

    assert sms.Destinations == [{"ToNumber": "+64211234567"}]


def test_add_destination_with_dict_appends_as_is(api_user):
    sms = SMS(api_user)
    sms.AddDestination({"ToNumber": "+64211234567", "FirstName": "Alice"})

    assert sms.Destinations == [{"ToNumber": "+64211234567", "FirstName": "Alice"}]


def test_add_destinations_with_mixed_list_adds_each_item(api_user):
    sms = SMS(api_user)
    sms.AddDestinations(["+64211234567", {"ToNumber": "+64221234567", "FirstName": "Bob"}])

    assert sms.Destinations == [{"ToNumber": "+64211234567"}, {"ToNumber": "+64221234567", "FirstName": "Bob"}]


def test_add_destination_with_contact_id(api_user):
    sms = SMS(api_user)
    sms.AddDestination(contact_id="6000000b-f002-4007-b00a-c00000000001")

    assert sms.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_destination_with_group_id(api_user):
    sms = SMS(api_user)
    sms.AddDestination(group_id="4000000b-f002-4007-b00a-c00000000002")

    assert sms.Destinations == [{"GroupID": "4000000b-f002-4007-b00a-c00000000002"}]


def test_add_destination_rejects_unknown_dict_key(api_user):
    sms = SMS(api_user)
    with pytest.raises(ValueError, match="ToNunber"):
        sms.AddDestination({"ToNunber": "+64211234567"})


def test_add_destination_accepts_a_destination_instance(api_user):
    sms = SMS(api_user)
    sms.AddDestination(Destination(ToNumber="+64211234567", FirstName="Alice"))

    assert sms.Destinations == [{"ToNumber": "+64211234567", "FirstName": "Alice"}]


def test_add_destination_accepts_mobile_phone(api_user):
    sms = SMS(api_user)
    sms.AddDestination({"MobilePhone": "+64211234567"})

    assert sms.Destinations == [{"MobilePhone": "+64211234567"}]


def test_send_message_rejects_destination_with_unknown_key(api_user):
    sms = SMS(api_user)
    result = sms.SendMessage(Message="Hi", Destinations=[{"ToNunber": "+64211234567"}])

    assert result.Result == "Failed"
    assert "ToNunber" in result.ErrorMessage[0]


def test_add_destination_chains(api_user):
    sms = SMS(api_user)
    result = sms.AddDestination("+64211234567").AddDestination("+64221234567")

    assert result is sms
    assert len(sms.Destinations) == 2


def test_add_attachment_appends_to_files(api_user):
    sms = SMS(api_user)
    sms.AddAttachment("test.pdf", "base64data==")

    assert sms.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_add_attachment_accepts_file_attachment_instance(api_user):
    sms = SMS(api_user)
    sms.AddAttachment(FileAttachment(Name="test.pdf", Data="base64data=="))

    assert sms.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_add_attachment_accepts_dict(api_user):
    sms = SMS(api_user)
    sms.AddAttachment({"Name": "test.pdf", "Data": "base64data=="})

    assert sms.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_add_attachment_accepts_single_real_path_string(tmp_path, api_user):
    path = tmp_path / "test.pdf"
    path.write_bytes(b"pdf-bytes")
    sms = SMS(api_user)

    sms.AddAttachment(str(path))

    assert sms.Files[0]["Name"] == "test.pdf"


def test_add_attachment_two_arg_form_with_literal_base64_never_warns(api_user, recwarn):
    sms = SMS(api_user)
    sms.AddAttachment("test.pdf", "base64data==")

    assert sms.Files == [{"Name": "test.pdf", "Data": "base64data=="}]
    assert len(recwarn) == 0


def test_add_attachment_two_arg_form_with_real_path_data_has_no_warning(tmp_path, api_user, recwarn):
    path = tmp_path / "real.pdf"
    path.write_bytes(b"pdf-bytes")
    sms = SMS(api_user)

    sms.AddAttachment("Custom Name.pdf", str(path))

    assert sms.Files[0]["Name"] == "Custom Name.pdf"
    assert len(recwarn) == 0


def test_build_returns_independent_copy(api_user):
    sms = SMS(api_user)
    sms.Message = "Hi"
    sms.AddDestination("+64211234567")

    model = sms.Build()

    assert model.Message == "Hi"
    assert model.Destinations == [{"ToNumber": "+64211234567"}]

    # mutating the builder after Build() must not affect the already-returned model
    sms.AddDestination("+64221234567")
    assert len(model.Destinations) == 1
    assert len(sms.Destinations) == 2

    # mutating a destination dict already captured by Build() must not leak through either
    sms.Destinations[0]["ToNumber"] = "+64299999999"
    assert model.Destinations[0]["ToNumber"] == "+64211234567"


def test_builder_chain_then_send_message(api_user):
    sms = SMS(api_user)
    sms.Set(Message="Hi [[FirstName]]", Reference="Builder test").AddDestination("+64211234567").AddDestination(
        {"ToNumber": "+64221234567", "FirstName": "Bob"}
    )

    body = sms._build_request_body()

    assert body["Message"] == "Hi [[FirstName]]"
    assert body["Reference"] == "Builder test"
    assert body["Destinations"] == [{"ToNumber": "+64211234567"}, {"ToNumber": "+64221234567", "FirstName": "Bob"}]


@responses_lib.activate
def test_send_message_accepts_prebuilt_model(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/sms",
        json={"MessageID": "msg-010"},
        status=200,
    )

    builder = SMS(api_user)
    model = builder.Set(Message="From model").AddDestination("+64211234567").Build()

    sms = SMS(api_user)
    result = sms.SendMessage(model)

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["Message"] == "From model"
    assert sent_body["Destinations"] == [{"ToNumber": "+64211234567"}]


@responses_lib.activate
def test_send_message_accepts_prebuilt_dict(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/sms",
        json={"MessageID": "msg-011"},
        status=200,
    )

    sms = SMS(api_user)
    result = sms.SendMessage({"Message": "From dict", "Destinations": [{"ToNumber": "+64211234567"}]})

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["Message"] == "From dict"


def test_send_message_rejects_invalid_model_type(api_user):
    sms = SMS(api_user)
    result = sms.SendMessage(model=12345)

    assert result.Result == "Failed"
    assert "12345" in result.ErrorMessage[0] or "int" in result.ErrorMessage[0]


def test_send_message_rejects_dict_model_with_unknown_key(api_user):
    sms = SMS(api_user)
    result = sms.SendMessage({"Bogus": "x"})

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


@responses_lib.activate
def test_send_message_dict_model_does_not_inherit_residual_set_state(api_user):
    sms = SMS(api_user)
    sms.Set(Reference="stale reference from a prior builder call")

    mock_endpoint(
        responses_lib.POST,
        "/sms",
        json={"MessageID": "msg-013"},
        status=200,
    )

    result = sms.SendMessage({"Message": "Fresh message", "Destinations": [{"ToNumber": "+64211234567"}]})

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert "Reference" not in sent_body


@responses_lib.activate
def test_send_message_model_plus_kwargs_kwargs_supplement_model(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/sms",
        json={"MessageID": "msg-012"},
        status=200,
    )

    model = SMS(api_user).Set(Message="Base").AddDestination("+64211234567").Build()

    sms = SMS(api_user)
    result = sms.SendMessage(model, Reference="Added on top")

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["Message"] == "Base"
    assert sent_body["Reference"] == "Added on top"


@responses_lib.activate
def test_send_message_kwargs_only_still_works_unchanged(api_user):
    # Regression guard: the pre-existing kwargs-only call style must be completely unaffected.
    mock_endpoint(
        responses_lib.POST,
        "/sms",
        json={"MessageID": "msg-013"},
        status=200,
    )

    sms = SMS(api_user)
    result = sms.SendMessage(Message="Old style", Destinations=[{"ToNumber": "+64211234567"}])

    assert result.Result == "Success"


@responses_lib.activate
def test_status_accepts_new_pascalcase_kwarg(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/sms/msg-001",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    sms = SMS(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            sms.Status(MessageID="msg-001")
        except TypeError as exc:
            pytest.fail(f"MessageID kwarg not accepted: {exc}")


@responses_lib.activate
def test_status_old_snake_case_kwarg_still_works_with_warning(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/sms/msg-001",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    sms = SMS(api_user)
    with pytest.warns(DeprecationWarning, match="message_id"):
        sms.Status(message_id="msg-001")


@responses_lib.activate
def test_received_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/sms/received",
        json={"Result": "Success", "TotalRecords": 0, "Messages": []},
        status=200,
    )

    sms = SMS(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            sms.Received(TimePeriod=10, RecordsPerPage=5, Page=2)
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


def test_add_destination_new_pascalcase_kwargs_accepted(api_user):
    sms = SMS(api_user)
    sms.AddDestination(ContactID="6000000b-f002-4007-b00a-c00000000001")
    assert sms.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_destination_old_snake_case_kwarg_still_works_with_warning(api_user):
    sms = SMS(api_user)
    with pytest.warns(DeprecationWarning, match="contact_id"):
        sms.AddDestination(contact_id="6000000b-f002-4007-b00a-c00000000001")
    assert sms.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_attachment_new_pascalcase_kwargs_accepted(api_user):
    sms = SMS(api_user)
    sms.AddAttachment(Name="test.pdf", Data="base64data==")
    assert sms.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_old_sms_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="SMSResponseDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.sms_response import SMSResponseDTO

    from tnzapi.api.v300.messaging.models.responses.sms_response import SMSResponse
    assert SMSResponseDTO is SMSResponse


def test_old_sms_status_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="SMSStatusDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.sms_status import SMSStatusDTO

    from tnzapi.api.v300.messaging.models.responses.sms_status import SMSStatus
    assert SMSStatusDTO is SMSStatus


def test_old_sms_action_result_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="SMSActionResultDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.sms_action_result import SMSActionResultDTO

    from tnzapi.api.v300.messaging.models.responses.sms_action_result import SMSActionResult
    assert SMSActionResultDTO is SMSActionResult


def test_old_sms_received_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="SMSReceivedDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.sms_received import SMSReceivedDTO

    from tnzapi.api.v300.messaging.models.responses.sms_received import SMSReceived
    assert SMSReceivedDTO is SMSReceived


def test_old_sms_request_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="SMSRequestDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.requests.sms_request import SMSRequestDTO

    from tnzapi.api.v300.messaging.models.requests.sms_request import SMSRequest
    assert SMSRequestDTO is SMSRequest
