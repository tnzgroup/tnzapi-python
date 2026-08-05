import json
import warnings

import pytest
import responses as responses_lib

from tnzapi.api.v300.messaging.builders.whatsapp import WhatsApp
from tnzapi.core.auth import TNZApiUser
from tnzapi.core.destination import Destination
from tnzapi.core.file_attachment import FileAttachment
from tests.conftest import mock_endpoint


def test_add_destinations_loops_over_items_calling_add_destination(api_user):
    via_singular = WhatsApp(api_user)
    via_singular.AddDestination("+64211111111")
    via_singular.AddDestination("+64211111112")

    via_plural = WhatsApp(api_user)
    result = via_plural.AddDestinations(["+64211111111", "+64211111112"])

    assert result is via_plural
    assert via_plural.Destinations == via_singular.Destinations


def test_add_destinations_accepts_a_tuple(api_user):
    via_singular = WhatsApp(api_user)
    via_singular.AddDestination("+64211111111")
    via_singular.AddDestination("+64211111112")

    via_plural = WhatsApp(api_user)
    result = via_plural.AddDestinations(("+64211111111", "+64211111112"))

    assert result is via_plural
    assert via_plural.Destinations == via_singular.Destinations


def test_add_destinations_rejects_a_bare_string(api_user):
    wa = WhatsApp(api_user)
    with pytest.raises(TypeError):
        wa.AddDestinations("+64211111111")


def test_add_destinations_rejects_a_dict(api_user):
    wa = WhatsApp(api_user)
    with pytest.raises(TypeError):
        wa.AddDestinations({"ToNumber": "+64211111111"})


def test_add_destination_rejects_a_list(api_user):
    wa = WhatsApp(api_user)
    with pytest.raises(TypeError):
        wa.AddDestination(["+64211111111", "+64211111112"])


def test_add_attachments_accepts_a_list_of_bare_paths(api_user, tmp_path):
    path_a = tmp_path / "a.txt"
    path_a.write_text("a")
    path_b = tmp_path / "b.txt"
    path_b.write_text("b")

    via_singular = WhatsApp(api_user)
    via_singular.AddAttachment(str(path_a))
    via_singular.AddAttachment(str(path_b))

    via_plural = WhatsApp(api_user)
    result = via_plural.AddAttachments([str(path_a), str(path_b)])

    assert result is via_plural
    assert via_plural.Files == via_singular.Files


def test_add_attachments_accepts_a_tuple(api_user, tmp_path):
    path_a = tmp_path / "a.txt"
    path_a.write_text("a")
    path_b = tmp_path / "b.txt"
    path_b.write_text("b")

    via_singular = WhatsApp(api_user)
    via_singular.AddAttachment(str(path_a))
    via_singular.AddAttachment(str(path_b))

    via_plural = WhatsApp(api_user)
    result = via_plural.AddAttachments((str(path_a), str(path_b)))

    assert result is via_plural
    assert via_plural.Files == via_singular.Files


def test_add_attachments_rejects_a_bare_string(api_user):
    wa = WhatsApp(api_user)
    with pytest.raises(TypeError):
        wa.AddAttachments("path/to/doc.pdf")


def test_add_attachments_rejects_a_dict(api_user):
    wa = WhatsApp(api_user)
    with pytest.raises(TypeError):
        wa.AddAttachments({"Name": "doc.pdf", "Data": "ZGF0YQ=="})


def test_add_attachments_accepts_a_list_of_file_attachment_instances(api_user):
    via_singular = WhatsApp(api_user)
    via_singular.AddAttachment(FileAttachment(Name="a.pdf", Data="ZGF0YQ=="))
    via_singular.AddAttachment(FileAttachment(Name="b.pdf", Data="ZGF0YQ=="))

    via_plural = WhatsApp(api_user)
    result = via_plural.AddAttachments([
        FileAttachment(Name="a.pdf", Data="ZGF0YQ=="),
        FileAttachment(Name="b.pdf", Data="ZGF0YQ=="),
    ])

    assert result is via_plural
    assert via_plural.Files == via_singular.Files


def test_fallback_mode_accepts_a_list_and_joins_it(api_user):
    wa = WhatsApp(api_user)
    wa.Message = "hi"
    wa.TemplateID = "tmpl-1"
    wa.FromNumber = "+6495005000"
    wa.Destinations = [{"ToNumber": "+64211111111"}]
    wa.Set(FallbackMode=["Voice", "SMS"])

    assert wa._build_request_body()["FallbackMode"] == "Voice, SMS"


def test_fallback_mode_single_string_still_works_unchanged(api_user):
    wa = WhatsApp(api_user)
    wa.Message = "hi"
    wa.TemplateID = "tmpl-1"
    wa.FromNumber = "+6495005000"
    wa.Destinations = [{"ToNumber": "+64211111111"}]
    wa.Set(FallbackMode="SMS")

    assert wa._build_request_body()["FallbackMode"] == "SMS"


def test_send_message_builds_correct_request_body(api_user):
    wa = WhatsApp(api_user)
    wa.TemplateID = "123e4567-e89b-12d3-a456-426614174000"
    wa.Message = "Hello world"
    wa.FromNumber = "+6495006000"
    wa.Destinations = [{"ToNumber": "+64211234567"}]

    body = wa._build_request_body()

    assert body["TemplateID"] == "123e4567-e89b-12d3-a456-426614174000"
    assert body["Message"] == "Hello world"
    assert body["FromNumber"] == "+6495006000"


def test_send_message_rejects_unknown_kwarg(api_user):
    wa = WhatsApp(api_user)
    result = wa.SendMessage(
        Bogus="x",
        TemplateID="123e4567-e89b-12d3-a456-426614174000",
        Message="hi",
        FromNumber="+6495006000",
        Destination="+64211234567",
    )

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


def test_send_message_rejects_missing_destination(api_user):
    wa = WhatsApp(api_user)
    result = wa.SendMessage(
        TemplateID="123e4567-e89b-12d3-a456-426614174000", Message="hi", FromNumber="+6495006000",
    )

    assert result.Result == "Failed"
    assert "Destinations" in result.ErrorMessage[0]


def test_received_rejects_time_period_out_of_range(api_user):
    wa = WhatsApp(api_user)

    result = wa.Received(TimePeriod=1441)

    assert result.Result == "Failed"
    assert "TimePeriod" in result.ErrorMessage[0]


def test_send_message_rejects_missing_template_id(api_user):
    wa = WhatsApp(api_user)
    result = wa.SendMessage(Message="hi", FromNumber="+6495006000", Destination="+64211234567")

    assert result.Result == "Failed"
    assert "TemplateID" in result.ErrorMessage[0]


def test_send_message_rejects_missing_message(api_user):
    wa = WhatsApp(api_user)
    result = wa.SendMessage(
        TemplateID="123e4567-e89b-12d3-a456-426614174000", FromNumber="+6495006000", Destination="+64211234567"
    )

    assert result.Result == "Failed"
    assert "Message" in result.ErrorMessage[0]


def test_send_message_rejects_missing_from_number(api_user):
    wa = WhatsApp(api_user)
    result = wa.SendMessage(
        TemplateID="123e4567-e89b-12d3-a456-426614174000", Message="hi", Destination="+64211234567"
    )

    assert result.Result == "Failed"
    assert "FromNumber" in result.ErrorMessage[0]


@responses_lib.activate
def test_send_message_returns_message_id_on_200_with_no_result_field(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/whatsapp",
        json={"MessageID": "msg-001"},
        status=200,
    )

    wa = WhatsApp(api_user)
    result = wa.SendMessage(
        TemplateID="123e4567-e89b-12d3-a456-426614174000",
        Message="Hi",
        FromNumber="+6495006000",
        Destination="+64211234567",
    )

    assert result.Result == "Success"
    assert result.MessageID == "msg-001"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["TemplateID"] == "123e4567-e89b-12d3-a456-426614174000"


@responses_lib.activate
def test_send_message_401_maps_to_unauthorized(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/whatsapp",
        json={"ErrorMessage": ["Access denied: Auth Token or credentials are incorrect or have expired."]},
        status=401,
    )

    wa = WhatsApp(api_user)
    result = wa.SendMessage(
        TemplateID="123e4567-e89b-12d3-a456-426614174000",
        Message="Hi",
        FromNumber="+6495006000",
        Destination="+64211234567",
    )

    assert result.Result == "Unauthorized"


@responses_lib.activate
def test_status_returns_message_detail_with_recipients(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/whatsapp/msg-001",
        json={
            "MessageID": "msg-001",
            "JobStatus": "Completed",
            "Recipients": [
                {"Type": "WhatsApp", "DestSeq": "00000001", "Destination": "+64211234567", "Status": "Success", "SMSReplies": []}
            ],
        },
        status=200,
    )

    wa = WhatsApp(api_user)
    result = wa.Status("msg-001")

    assert result.Result == "Success"
    assert result.Recipients[0]["SMSReplies"] == []


@responses_lib.activate
def test_status_404_maps_to_record_not_found(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/whatsapp/missing-id",
        json={"ErrorMessage": ["Message not found."]},
        status=404,
    )

    wa = WhatsApp(api_user)
    result = wa.Status("missing-id")

    assert result.Result == "RecordNotFound"


@responses_lib.activate
def test_reschedule_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/whatsapp/msg-001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Delayed", "Action": "Reschedule"},
        status=200,
    )

    wa = WhatsApp(api_user)
    result = wa.Reschedule("msg-001", "2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert result.Action == "Reschedule"


@responses_lib.activate
def test_abort_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/whatsapp/msg-001/abort",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Completed", "Action": "Abort"},
        status=200,
    )

    wa = WhatsApp(api_user)
    result = wa.Abort("msg-001")

    assert result.Result == "Success"
    assert result.Action == "Abort"


@responses_lib.activate
def test_received_returns_messages(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/whatsapp/received",
        json={
            "TotalRecords": 1,
            "RecordsPerPage": 20,
            "PageCount": 1,
            "Page": 1,
            "Messages": [{"ReceivedID": "a1b2c3d4-e5f6-7890-1234-567890abcdee", "From": "+6421000001", "MessageText": "Hi there"}],
        },
        status=200,
    )

    wa = WhatsApp(api_user)
    result = wa.Received(time_period=10)

    assert result.Result == "Success"
    assert result.Messages[0]["MessageText"] == "Hi there"


def test_set_applies_multiple_fields_and_returns_self(api_user):
    wa = WhatsApp(api_user)
    returned = wa.Set(Message="Hi", Reference="Test")

    assert returned is wa
    assert wa.Message == "Hi"
    assert wa.Reference == "Test"


def test_set_raises_on_unknown_field(api_user):
    wa = WhatsApp(api_user)
    with pytest.raises(ValueError):
        wa.Set(Bogus="x")


def test_add_destination_with_string_wraps_as_to_number(api_user):
    wa = WhatsApp(api_user)
    wa.AddDestination("+64211234567")

    assert wa.Destinations == [{"ToNumber": "+64211234567"}]


def test_add_destination_with_dict_appends_as_is(api_user):
    wa = WhatsApp(api_user)
    wa.AddDestination({"ToNumber": "+64211234567", "FirstName": "Alice"})

    assert wa.Destinations == [{"ToNumber": "+64211234567", "FirstName": "Alice"}]


def test_add_destinations_with_mixed_list_adds_each_item(api_user):
    wa = WhatsApp(api_user)
    wa.AddDestinations(["+64211234567", {"ToNumber": "+64221234567", "FirstName": "Bob"}])

    assert wa.Destinations == [{"ToNumber": "+64211234567"}, {"ToNumber": "+64221234567", "FirstName": "Bob"}]


def test_add_destination_with_contact_id(api_user):
    wa = WhatsApp(api_user)
    wa.AddDestination(contact_id="6000000b-f002-4007-b00a-c00000000001")

    assert wa.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_destination_with_group_id(api_user):
    wa = WhatsApp(api_user)
    wa.AddDestination(group_id="4000000b-f002-4007-b00a-c00000000002")

    assert wa.Destinations == [{"GroupID": "4000000b-f002-4007-b00a-c00000000002"}]


def test_add_destination_rejects_unknown_dict_key(api_user):
    wa = WhatsApp(api_user)
    with pytest.raises(ValueError, match="ToNunber"):
        wa.AddDestination({"ToNunber": "+64211234567"})


def test_add_destination_accepts_a_destination_instance(api_user):
    wa = WhatsApp(api_user)
    wa.AddDestination(Destination(ToNumber="+64211234567", Custom1="value1"))

    assert wa.Destinations == [{"ToNumber": "+64211234567", "Custom1": "value1"}]


def test_add_destination_accepts_mobile_phone(api_user):
    wa = WhatsApp(api_user)
    wa.AddDestination({"MobilePhone": "+64211234567"})

    assert wa.Destinations == [{"MobilePhone": "+64211234567"}]


def test_send_message_rejects_destination_with_unknown_key(api_user):
    wa = WhatsApp(api_user)
    result = wa.SendMessage(
        TemplateID="tmpl-1", Message="Hi", FromNumber="+6495005000",
        Destinations=[{"ToNunber": "+64211234567"}],
    )

    assert result.Result == "Failed"
    assert "ToNunber" in result.ErrorMessage[0]


def test_add_destination_chains(api_user):
    wa = WhatsApp(api_user)
    result = wa.AddDestination("+64211234567").AddDestination("+64221234567")

    assert result is wa
    assert len(wa.Destinations) == 2


def test_add_attachment_appends_to_files(api_user):
    wa = WhatsApp(api_user)
    wa.AddAttachment("test.pdf", "base64data==")

    assert wa.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_add_attachment_accepts_file_attachment_instance(api_user):
    wa = WhatsApp(api_user)
    wa.AddAttachment(FileAttachment(Name="test.pdf", Data="base64data=="))

    assert wa.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_add_attachment_accepts_dict(api_user):
    wa = WhatsApp(api_user)
    wa.AddAttachment({"Name": "test.pdf", "Data": "base64data=="})

    assert wa.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_add_attachment_accepts_single_real_path_string(tmp_path, api_user):
    path = tmp_path / "test.pdf"
    path.write_bytes(b"pdf-bytes")
    wa = WhatsApp(api_user)

    wa.AddAttachment(str(path))

    assert wa.Files[0]["Name"] == "test.pdf"


def test_add_attachment_two_arg_form_with_literal_base64_never_warns(api_user, recwarn):
    wa = WhatsApp(api_user)
    wa.AddAttachment("test.pdf", "base64data==")

    assert wa.Files == [{"Name": "test.pdf", "Data": "base64data=="}]
    assert len(recwarn) == 0


def test_add_attachment_two_arg_form_with_real_path_data_has_no_warning(tmp_path, api_user, recwarn):
    path = tmp_path / "real.pdf"
    path.write_bytes(b"pdf-bytes")
    wa = WhatsApp(api_user)

    wa.AddAttachment("Custom Name.pdf", str(path))

    assert wa.Files[0]["Name"] == "Custom Name.pdf"
    assert len(recwarn) == 0


def test_build_returns_independent_copy(api_user):
    wa = WhatsApp(api_user)
    wa.TemplateID = "123e4567-e89b-12d3-a456-426614174000"
    wa.AddDestination("+64211234567")

    model = wa.Build()

    assert model.TemplateID == "123e4567-e89b-12d3-a456-426614174000"
    assert model.Destinations == [{"ToNumber": "+64211234567"}]

    # mutating the builder after Build() must not affect the already-returned model
    wa.AddDestination("+64221234567")
    assert len(model.Destinations) == 1
    assert len(wa.Destinations) == 2

    # mutating a destination dict already captured by Build() must not leak through either
    wa.Destinations[0]["ToNumber"] = "+64299999999"
    assert model.Destinations[0]["ToNumber"] == "+64211234567"


@responses_lib.activate
def test_send_message_accepts_prebuilt_model(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/whatsapp",
        json={"MessageID": "msg-010"},
        status=200,
    )

    builder = WhatsApp(api_user)
    model = (
        builder.Set(
            TemplateID="123e4567-e89b-12d3-a456-426614174000",
            Message="From model",
            FromNumber="+6495006000",
        )
        .AddDestination("+64211234567")
        .Build()
    )

    wa = WhatsApp(api_user)
    result = wa.SendMessage(model)

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["Message"] == "From model"
    assert sent_body["Destinations"] == [{"ToNumber": "+64211234567"}]


@responses_lib.activate
def test_send_message_accepts_prebuilt_dict(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/whatsapp",
        json={"MessageID": "msg-011"},
        status=200,
    )

    wa = WhatsApp(api_user)
    result = wa.SendMessage(
        {
            "TemplateID": "123e4567-e89b-12d3-a456-426614174000",
            "Message": "From dict",
            "FromNumber": "+6495006000",
            "Destinations": [{"ToNumber": "+64211234567"}],
        }
    )

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["Message"] == "From dict"


def test_send_message_rejects_invalid_model_type(api_user):
    wa = WhatsApp(api_user)
    result = wa.SendMessage(model=12345)

    assert result.Result == "Failed"
    assert "12345" in result.ErrorMessage[0] or "int" in result.ErrorMessage[0]


def test_send_message_rejects_dict_model_with_unknown_key(api_user):
    wa = WhatsApp(api_user)
    result = wa.SendMessage({"Bogus": "x"})

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


@responses_lib.activate
def test_send_message_dict_model_does_not_inherit_residual_set_state(api_user):
    wa = WhatsApp(api_user)
    wa.Set(Reference="stale reference from a prior builder call")

    mock_endpoint(
        responses_lib.POST,
        "/whatsapp",
        json={"MessageID": "msg-013"},
        status=200,
    )

    result = wa.SendMessage(
        {
            "TemplateID": "123e4567-e89b-12d3-a456-426614174000",
            "Message": "Fresh message",
            "FromNumber": "+6495006000",
            "Destinations": [{"ToNumber": "+64211234567"}],
        }
    )

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert "Reference" not in sent_body


@responses_lib.activate
def test_send_message_kwargs_only_still_works_unchanged(api_user):
    # Regression guard: the pre-existing kwargs-only call style must be completely unaffected.
    mock_endpoint(
        responses_lib.POST,
        "/whatsapp",
        json={"MessageID": "msg-013"},
        status=200,
    )

    wa = WhatsApp(api_user)
    result = wa.SendMessage(
        TemplateID="123e4567-e89b-12d3-a456-426614174000",
        Message="Old style",
        FromNumber="+6495006000",
        Destination="+64211234567",
    )

    assert result.Result == "Success"


def test_send_message_model_still_enforces_required_fields(api_user):
    model = (
        WhatsApp(api_user).Set(Message="Hi").AddDestination("+64211234567").Build()
    )  # missing TemplateID and FromNumber

    wa = WhatsApp(api_user)
    result = wa.SendMessage(model)

    assert result.Result == "Failed"
    assert "TemplateID" in result.ErrorMessage[0]


def test_send_message_model_still_enforces_from_number(api_user):
    model = (
        WhatsApp(api_user)
        .Set(TemplateID="123e4567-e89b-12d3-a456-426614174000", Message="Hi")
        .AddDestination("+64211234567")
        .Build()
    )  # missing FromNumber only

    wa = WhatsApp(api_user)
    result = wa.SendMessage(model)

    assert result.Result == "Failed"
    assert "FromNumber" in result.ErrorMessage[0]


@responses_lib.activate
def test_status_accepts_new_pascalcase_kwarg(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/whatsapp/msg-001",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    whatsapp = WhatsApp(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            whatsapp.Status(MessageID="msg-001")
        except TypeError as exc:
            pytest.fail(f"MessageID kwarg not accepted: {exc}")


@responses_lib.activate
def test_status_old_snake_case_kwarg_still_works_with_warning(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/whatsapp/msg-001",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    whatsapp = WhatsApp(api_user)
    with pytest.warns(DeprecationWarning, match="message_id"):
        whatsapp.Status(message_id="msg-001")


@responses_lib.activate
def test_received_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/whatsapp/received",
        json={"Result": "Success", "TotalRecords": 0, "Messages": []},
        status=200,
    )

    whatsapp = WhatsApp(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            whatsapp.Received(TimePeriod=10, RecordsPerPage=5, Page=2)
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


def test_add_destination_new_pascalcase_kwargs_accepted(api_user):
    whatsapp = WhatsApp(api_user)
    whatsapp.AddDestination(ContactID="6000000b-f002-4007-b00a-c00000000001")
    assert whatsapp.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_destination_old_snake_case_kwarg_still_works_with_warning(api_user):
    whatsapp = WhatsApp(api_user)
    with pytest.warns(DeprecationWarning, match="contact_id"):
        whatsapp.AddDestination(contact_id="6000000b-f002-4007-b00a-c00000000001")
    assert whatsapp.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_attachment_new_pascalcase_kwargs_accepted(api_user):
    whatsapp = WhatsApp(api_user)
    whatsapp.AddAttachment(Name="test.pdf", Data="base64data==")
    assert whatsapp.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_old_whatsapp_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="WhatsAppResponseDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.whatsapp_response import WhatsAppResponseDTO

    from tnzapi.api.v300.messaging.models.responses.whatsapp_response import WhatsAppResponse
    assert WhatsAppResponseDTO is WhatsAppResponse


def test_old_whatsapp_status_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="WhatsAppStatusDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.whatsapp_status import WhatsAppStatusDTO

    from tnzapi.api.v300.messaging.models.responses.whatsapp_status import WhatsAppStatus
    assert WhatsAppStatusDTO is WhatsAppStatus


def test_old_whatsapp_action_result_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="WhatsAppActionResultDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.whatsapp_action_result import WhatsAppActionResultDTO

    from tnzapi.api.v300.messaging.models.responses.whatsapp_action_result import WhatsAppActionResult
    assert WhatsAppActionResultDTO is WhatsAppActionResult


def test_old_whatsapp_received_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="WhatsAppReceivedDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.whatsapp_received import WhatsAppReceivedDTO

    from tnzapi.api.v300.messaging.models.responses.whatsapp_received import WhatsAppReceived
    assert WhatsAppReceivedDTO is WhatsAppReceived


def test_old_whatsapp_request_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="WhatsAppRequestDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.requests.whatsapp_request import WhatsAppRequestDTO

    from tnzapi.api.v300.messaging.models.requests.whatsapp_request import WhatsAppRequest
    assert WhatsAppRequestDTO is WhatsAppRequest
