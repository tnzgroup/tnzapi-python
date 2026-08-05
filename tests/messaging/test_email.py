import json
import warnings

import pytest
import responses as responses_lib

from tnzapi.api.v300.messaging.builders.email import Email
from tnzapi.core.auth import TNZApiUser
from tnzapi.core.destination import Destination
from tnzapi.core.file_attachment import FileAttachment
from tests.conftest import mock_endpoint


def test_send_message_builds_correct_request_body(api_user):
    email = Email(api_user)
    email.EmailSubject = "Test"
    email.MessagePlain = "Hello world"
    email.Destinations = [{"EmailAddress": "test@example.com"}]

    body = email._build_request_body()

    assert body["EmailSubject"] == "Test"
    assert body["MessagePlain"] == "Hello world"
    assert body["Destinations"] == [{"EmailAddress": "test@example.com"}]


def test_add_destinations_loops_over_items_calling_add_destination(api_user):
    via_singular = Email(api_user)
    via_singular.AddDestination("a@example.com")
    via_singular.AddDestination("b@example.com")

    via_plural = Email(api_user)
    result = via_plural.AddDestinations(["a@example.com", "b@example.com"])

    assert result is via_plural
    assert via_plural.Destinations == via_singular.Destinations


def test_add_destinations_accepts_a_tuple(api_user):
    via_singular = Email(api_user)
    via_singular.AddDestination("a@example.com")
    via_singular.AddDestination("b@example.com")

    via_plural = Email(api_user)
    result = via_plural.AddDestinations(("a@example.com", "b@example.com"))

    assert result is via_plural
    assert via_plural.Destinations == via_singular.Destinations


def test_add_destinations_rejects_a_bare_string(api_user):
    email = Email(api_user)
    with pytest.raises(TypeError):
        email.AddDestinations("a@example.com")


def test_add_destinations_rejects_a_dict(api_user):
    email = Email(api_user)
    with pytest.raises(TypeError):
        email.AddDestinations({"EmailAddress": "a@example.com"})


def test_add_destination_rejects_a_list(api_user):
    email = Email(api_user)
    with pytest.raises(TypeError):
        email.AddDestination(["a@example.com", "b@example.com"])


def test_add_attachments_accepts_a_list_of_bare_paths(api_user, tmp_path):
    path_a = tmp_path / "a.txt"
    path_a.write_text("a")
    path_b = tmp_path / "b.txt"
    path_b.write_text("b")

    via_singular = Email(api_user)
    via_singular.AddAttachment(str(path_a))
    via_singular.AddAttachment(str(path_b))

    via_plural = Email(api_user)
    result = via_plural.AddAttachments([str(path_a), str(path_b)])

    assert result is via_plural
    assert via_plural.Files == via_singular.Files


def test_add_attachments_accepts_a_tuple(api_user, tmp_path):
    path_a = tmp_path / "a.txt"
    path_a.write_text("a")
    path_b = tmp_path / "b.txt"
    path_b.write_text("b")

    via_singular = Email(api_user)
    via_singular.AddAttachment(str(path_a))
    via_singular.AddAttachment(str(path_b))

    via_plural = Email(api_user)
    result = via_plural.AddAttachments((str(path_a), str(path_b)))

    assert result is via_plural
    assert via_plural.Files == via_singular.Files


def test_add_attachments_rejects_a_bare_string(api_user):
    email = Email(api_user)
    with pytest.raises(TypeError):
        email.AddAttachments("path/to/doc.pdf")


def test_add_attachments_rejects_a_dict(api_user):
    email = Email(api_user)
    with pytest.raises(TypeError):
        email.AddAttachments({"Name": "doc.pdf", "Data": "ZGF0YQ=="})


def test_add_attachments_accepts_a_list_of_file_attachment_instances(api_user):
    via_singular = Email(api_user)
    via_singular.AddAttachment(FileAttachment(Name="a.pdf", Data="ZGF0YQ=="))
    via_singular.AddAttachment(FileAttachment(Name="b.pdf", Data="ZGF0YQ=="))

    via_plural = Email(api_user)
    result = via_plural.AddAttachments([
        FileAttachment(Name="a.pdf", Data="ZGF0YQ=="),
        FileAttachment(Name="b.pdf", Data="ZGF0YQ=="),
    ])

    assert result is via_plural
    assert via_plural.Files == via_singular.Files


def test_set_destinations_converts_a_bare_string_using_email_address(api_user):
    email = Email(api_user)

    email.Set(Destinations=["test@example.com"])

    assert email.Destinations == [{"EmailAddress": "test@example.com"}]


def test_set_and_add_destination_produce_identical_output_for_the_same_string(api_user):
    via_set = Email(api_user)
    via_set.Set(Destinations=["test@example.com"])

    via_add_destination = Email(api_user)
    via_add_destination.AddDestination("test@example.com")

    assert via_set.Destinations == via_add_destination.Destinations


def test_send_message_rejects_unknown_kwarg(api_user):
    email = Email(api_user)
    result = email.SendMessage(Bogus="x", EmailSubject="Test", MessagePlain="hi", Destination="test@example.com")

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


def test_send_message_rejects_missing_destination(api_user):
    email = Email(api_user)
    result = email.SendMessage(MessagePlain="hi")

    assert result.Result == "Failed"
    assert "Destinations" in result.ErrorMessage[0]


def test_send_message_rejects_missing_message(api_user):
    email = Email(api_user)
    result = email.SendMessage(Destination="test@example.com")

    assert result.Result == "Failed"
    assert "MessagePlain" in result.ErrorMessage[0]


@responses_lib.activate
def test_send_message_accepts_contact_id_alone_as_destination(api_user):
    # docs/email.md documents ContactID as a standalone alternative to Destinations -
    # a regression guard for a real bug where the destination-required check only
    # looked at Destinations/Destination/EmailAddress, wrongly rejecting this.
    mock_endpoint(responses_lib.POST, "/email", json={"MessageID": "msg-001"}, status=200)

    email = Email(api_user)
    result = email.SendMessage(MessagePlain="hi", ContactID="c-001")

    assert result.Result == "Success"


@responses_lib.activate
def test_send_message_returns_message_id_on_200_with_no_result_field(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/email",
        json={"MessageID": "msg-001"},
        status=200,
    )

    email = Email(api_user)
    result = email.SendMessage(EmailSubject="Test", MessagePlain="Hi", Destination="test@example.com")

    assert result.Result == "Success"
    assert result.MessageID == "msg-001"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["EmailSubject"] == "Test"
    assert sent_body["Destination"] == "test@example.com"


@responses_lib.activate
def test_send_message_401_maps_to_unauthorized(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/email",
        json={"ErrorMessage": ["Access denied: Auth Token or credentials are incorrect or have expired."]},
        status=401,
    )

    email = Email(api_user)
    result = email.SendMessage(EmailSubject="Test", MessagePlain="Hi", Destination="test@example.com")

    assert result.Result == "Unauthorized"


@responses_lib.activate
def test_status_returns_message_detail_with_recipients(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/email/msg-001",
        json={
            "MessageID": "msg-001",
            "JobStatus": "Completed",
            "Recipients": [
                {"Type": "Email", "DestSeq": "00000001", "Destination": "test@example.com", "Status": "Success", "Result": "250 OK"}
            ],
        },
        status=200,
    )

    email = Email(api_user)
    result = email.Status("msg-001")

    assert result.Result == "Success"
    assert result.Recipients[0]["Destination"] == "test@example.com"


@responses_lib.activate
def test_status_404_maps_to_record_not_found(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/email/missing-id",
        json={"ErrorMessage": ["Message not found."]},
        status=404,
    )

    email = Email(api_user)
    result = email.Status("missing-id")

    assert result.Result == "RecordNotFound"


@responses_lib.activate
def test_reschedule_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/email/msg-001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Delayed", "Action": "Reschedule"},
        status=200,
    )

    email = Email(api_user)
    result = email.Reschedule("msg-001", "2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert result.Action == "Reschedule"
    assert json.loads(responses_lib.calls[0].request.body) == {"SendTime": "2026-08-01T09:00:00"}


@responses_lib.activate
def test_reschedule_escapes_message_id_in_path(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/email/msg%2F001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg/001", "Status": "Delayed", "Action": "Reschedule"},
        status=200,
    )

    email = Email(api_user)
    result = email.Reschedule("msg/001", "2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert responses_lib.calls[0].request.url == "https://api.tnz.co.nz/api/v3.00/email/msg%2F001/reschedule"


@responses_lib.activate
def test_abort_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/email/msg-001/abort",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Completed", "Action": "Abort"},
        status=200,
    )

    email = Email(api_user)
    result = email.Abort("msg-001")

    assert result.Result == "Success"
    assert result.Action == "Abort"


@responses_lib.activate
def test_resubmit_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/email/msg-001/resubmit",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Pending", "Action": "Resubmit"},
        status=200,
    )

    email = Email(api_user)
    result = email.Resubmit("msg-001", "2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert result.Action == "Resubmit"
    assert json.loads(responses_lib.calls[0].request.body) == {"SendTime": "2026-08-01T09:00:00"}


def test_set_applies_multiple_fields_and_returns_self(api_user):
    email = Email(api_user)
    returned = email.Set(EmailSubject="Hi", Reference="Test")

    assert returned is email
    assert email.EmailSubject == "Hi"
    assert email.Reference == "Test"


def test_set_raises_on_unknown_field(api_user):
    email = Email(api_user)
    with pytest.raises(ValueError):
        email.Set(Bogus="x")


def test_add_destination_with_string_wraps_as_email_address(api_user):
    email = Email(api_user)
    email.AddDestination("test@example.com")

    assert email.Destinations == [{"EmailAddress": "test@example.com"}]


def test_add_destination_with_dict_appends_as_is(api_user):
    email = Email(api_user)
    email.AddDestination({"EmailAddress": "test@example.com", "FirstName": "Alice"})

    assert email.Destinations == [{"EmailAddress": "test@example.com", "FirstName": "Alice"}]


def test_add_destinations_with_mixed_list_adds_each_item(api_user):
    email = Email(api_user)
    email.AddDestinations(["test@example.com", {"EmailAddress": "bob@example.com", "FirstName": "Bob"}])

    assert email.Destinations == [{"EmailAddress": "test@example.com"}, {"EmailAddress": "bob@example.com", "FirstName": "Bob"}]


def test_add_destination_with_contact_id(api_user):
    email = Email(api_user)
    email.AddDestination(contact_id="6000000b-f002-4007-b00a-c00000000001")

    assert email.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_destination_with_group_id(api_user):
    email = Email(api_user)
    email.AddDestination(group_id="4000000b-f002-4007-b00a-c00000000002")

    assert email.Destinations == [{"GroupID": "4000000b-f002-4007-b00a-c00000000002"}]


def test_add_destination_rejects_unknown_dict_key(api_user):
    email = Email(api_user)
    with pytest.raises(ValueError, match="EmailAddres"):
        email.AddDestination({"EmailAddres": "test@example.com"})


def test_add_destination_accepts_a_destination_instance(api_user):
    email = Email(api_user)
    email.AddDestination(Destination(EmailAddress="test@example.com", FirstName="Alice"))

    assert email.Destinations == [{"EmailAddress": "test@example.com", "FirstName": "Alice"}]


def test_send_message_rejects_destination_with_unknown_key(api_user):
    email = Email(api_user)
    result = email.SendMessage(MessagePlain="Hi", Destinations=[{"EmailAddres": "test@example.com"}])

    assert result.Result == "Failed"
    assert "EmailAddres" in result.ErrorMessage[0]


def test_add_destination_chains(api_user):
    email = Email(api_user)
    result = email.AddDestination("test@example.com").AddDestination("bob@example.com")

    assert result is email
    assert len(email.Destinations) == 2


def test_add_attachment_appends_to_files(api_user):
    email = Email(api_user)
    email.AddAttachment("test.pdf", "base64data==")

    assert email.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_add_attachment_accepts_file_attachment_instance(api_user):
    email = Email(api_user)
    email.AddAttachment(FileAttachment(Name="test.pdf", Data="base64data=="))

    assert email.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_add_attachment_accepts_dict(api_user):
    email = Email(api_user)
    email.AddAttachment({"Name": "test.pdf", "Data": "base64data=="})

    assert email.Files == [{"Name": "test.pdf", "Data": "base64data=="}]


def test_add_attachment_accepts_single_real_path_string(tmp_path, api_user):
    path = tmp_path / "test.pdf"
    path.write_bytes(b"pdf-bytes")
    email = Email(api_user)

    email.AddAttachment(str(path))

    assert email.Files[0]["Name"] == "test.pdf"


def test_add_attachment_two_arg_form_with_literal_base64_never_warns(api_user, recwarn):
    email = Email(api_user)
    email.AddAttachment("test.pdf", "base64data==")

    assert email.Files == [{"Name": "test.pdf", "Data": "base64data=="}]
    assert len(recwarn) == 0


def test_add_attachment_two_arg_form_with_real_path_data_has_no_warning(tmp_path, api_user, recwarn):
    path = tmp_path / "real.pdf"
    path.write_bytes(b"pdf-bytes")
    email = Email(api_user)

    email.AddAttachment("Custom Name.pdf", str(path))

    assert email.Files[0]["Name"] == "Custom Name.pdf"
    assert len(recwarn) == 0


def test_build_returns_independent_copy(api_user):
    email = Email(api_user)
    email.EmailSubject = "Hi"
    email.AddDestination("test@example.com")

    model = email.Build()

    assert model.EmailSubject == "Hi"
    assert model.Destinations == [{"EmailAddress": "test@example.com"}]

    # mutating the builder after Build() must not affect the already-returned model
    email.AddDestination("bob@example.com")
    assert len(model.Destinations) == 1
    assert len(email.Destinations) == 2

    # mutating a destination dict already captured by Build() must not leak through either
    email.Destinations[0]["EmailAddress"] = "changed@example.com"
    assert model.Destinations[0]["EmailAddress"] == "test@example.com"


def test_builder_chain_then_send_message(api_user):
    email = Email(api_user)
    email.Set(EmailSubject="Hi [[FirstName]]", Reference="Builder test").AddDestination("test@example.com").AddDestination(
        {"EmailAddress": "bob@example.com", "FirstName": "Bob"}
    )

    body = email._build_request_body()

    assert body["EmailSubject"] == "Hi [[FirstName]]"
    assert body["Reference"] == "Builder test"
    assert body["Destinations"] == [{"EmailAddress": "test@example.com"}, {"EmailAddress": "bob@example.com", "FirstName": "Bob"}]


@responses_lib.activate
def test_send_message_accepts_prebuilt_model(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/email",
        json={"MessageID": "msg-010"},
        status=200,
    )

    builder = Email(api_user)
    model = builder.Set(EmailSubject="From model", MessagePlain="Body").AddDestination("test@example.com").Build()

    email = Email(api_user)
    result = email.SendMessage(model)

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["EmailSubject"] == "From model"
    assert sent_body["Destinations"] == [{"EmailAddress": "test@example.com"}]


@responses_lib.activate
def test_send_message_accepts_prebuilt_dict(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/email",
        json={"MessageID": "msg-011"},
        status=200,
    )

    email = Email(api_user)
    result = email.SendMessage({
        "EmailSubject": "From dict",
        "MessagePlain": "Body",
        "Destinations": [{"EmailAddress": "test@example.com"}],
    })

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["EmailSubject"] == "From dict"


def test_send_message_rejects_invalid_model_type(api_user):
    email = Email(api_user)
    result = email.SendMessage(model=12345)

    assert result.Result == "Failed"
    assert "12345" in result.ErrorMessage[0] or "int" in result.ErrorMessage[0]


def test_send_message_rejects_dict_model_with_unknown_key(api_user):
    email = Email(api_user)
    result = email.SendMessage({"Bogus": "x"})

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


@responses_lib.activate
def test_send_message_dict_model_does_not_inherit_residual_set_state(api_user):
    email = Email(api_user)
    email.Set(Reference="stale reference from a prior builder call")

    mock_endpoint(
        responses_lib.POST,
        "/email",
        json={"MessageID": "msg-013"},
        status=200,
    )

    result = email.SendMessage({
        "EmailSubject": "Fresh subject",
        "MessagePlain": "Body",
        "Destinations": [{"EmailAddress": "test@example.com"}],
    })

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert "Reference" not in sent_body


@responses_lib.activate
def test_send_message_model_plus_kwargs_kwargs_supplement_model(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/email",
        json={"MessageID": "msg-012"},
        status=200,
    )

    model = Email(api_user).Set(EmailSubject="Base", MessagePlain="Body").AddDestination("test@example.com").Build()

    email = Email(api_user)
    result = email.SendMessage(model, Reference="Added on top")

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["EmailSubject"] == "Base"
    assert sent_body["Reference"] == "Added on top"


@responses_lib.activate
def test_send_message_kwargs_only_still_works_unchanged(api_user):
    # Regression guard: the pre-existing kwargs-only call style must be completely unaffected.
    mock_endpoint(
        responses_lib.POST,
        "/email",
        json={"MessageID": "msg-013"},
        status=200,
    )

    email = Email(api_user)
    result = email.SendMessage(
        EmailSubject="Old style", MessagePlain="Body", Destinations=[{"EmailAddress": "test@example.com"}]
    )

    assert result.Result == "Success"


@responses_lib.activate
def test_status_accepts_new_pascalcase_kwarg(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/email/msg-001",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    email = Email(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            email.Status(MessageID="msg-001")
        except TypeError as exc:
            pytest.fail(f"MessageID kwarg not accepted: {exc}")


@responses_lib.activate
def test_status_old_snake_case_kwarg_still_works_with_warning(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/email/msg-001",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    email = Email(api_user)
    with pytest.warns(DeprecationWarning, match="message_id"):
        email.Status(message_id="msg-001")


@responses_lib.activate
def test_reschedule_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/email/msg-001/reschedule",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    email = Email(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            email.Reschedule(MessageID="msg-001", SendTime="2026-08-01T09:00:00")
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_resubmit_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/email/msg-001/resubmit",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    email = Email(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            email.Resubmit(MessageID="msg-001", SendTime="2026-08-01T09:00:00")
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


def test_add_destination_new_pascalcase_kwargs_accepted(api_user):
    email = Email(api_user)
    email.AddDestination(ContactID="6000000b-f002-4007-b00a-c00000000001")
    assert email.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_destination_old_snake_case_kwarg_still_works_with_warning(api_user):
    email = Email(api_user)
    with pytest.warns(DeprecationWarning, match="contact_id"):
        email.AddDestination(contact_id="6000000b-f002-4007-b00a-c00000000001")
    assert email.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_attachment_new_pascalcase_kwargs_accepted(api_user):
    email = Email(api_user)
    email.AddAttachment(Name="test.pdf", Data="base64data==")
    assert email.Files == [{"Name": "test.pdf", "Data": "base64data=="}]

def test_old_email_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="EmailResponseDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.email_response import EmailResponseDTO

    from tnzapi.api.v300.messaging.models.responses.email_response import EmailResponse
    assert EmailResponseDTO is EmailResponse


def test_old_email_status_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="EmailStatusDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.email_status import EmailStatusDTO

    from tnzapi.api.v300.messaging.models.responses.email_status import EmailStatus
    assert EmailStatusDTO is EmailStatus


def test_old_email_action_result_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="EmailActionResultDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.email_action_result import EmailActionResultDTO

    from tnzapi.api.v300.messaging.models.responses.email_action_result import EmailActionResult
    assert EmailActionResultDTO is EmailActionResult


def test_old_email_request_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="EmailRequestDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.requests.email_request import EmailRequestDTO

    from tnzapi.api.v300.messaging.models.requests.email_request import EmailRequest
    assert EmailRequestDTO is EmailRequest
