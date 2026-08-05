import json
import warnings

import pytest
import responses as responses_lib

from tnzapi.api.v300.messaging.builders.tts import TTS
from tnzapi.core.auth import TNZApiUser
from tnzapi.core.destination import Destination
from tests.conftest import mock_endpoint


def test_send_message_builds_correct_request_body(api_user):
    tts = TTS(api_user)
    tts.MessageToPeople = "Hello world"
    tts.Destinations = [{"MainPhone": "+64211234567"}]
    tts.Keypads = [{"Tone": 1, "Play": "You pressed 1", "RouteNumber": "+6491234567"}]

    body = tts._build_request_body()

    assert body["MessageToPeople"] == "Hello world"
    assert body["Keypads"] == [{"Tone": 1, "Play": "You pressed 1", "RouteNumber": "+6491234567"}]


def test_add_destinations_loops_over_items_calling_add_destination(api_user):
    via_singular = TTS(api_user)
    via_singular.AddDestination("+64211234567")
    via_singular.AddDestination("+64211234568")

    via_plural = TTS(api_user)
    result = via_plural.AddDestinations(["+64211234567", "+64211234568"])

    assert result is via_plural
    assert via_plural.Destinations == via_singular.Destinations


def test_add_destinations_accepts_a_tuple(api_user):
    via_singular = TTS(api_user)
    via_singular.AddDestination("+64211234567")
    via_singular.AddDestination("+64211234568")

    via_plural = TTS(api_user)
    result = via_plural.AddDestinations(("+64211234567", "+64211234568"))

    assert result is via_plural
    assert via_plural.Destinations == via_singular.Destinations


def test_add_destinations_rejects_a_bare_string(api_user):
    tts = TTS(api_user)
    with pytest.raises(TypeError):
        tts.AddDestinations("+64211234567")


def test_add_destinations_rejects_a_dict(api_user):
    tts = TTS(api_user)
    with pytest.raises(TypeError):
        tts.AddDestinations({"ToNumber": "+64211234567"})


def test_add_destination_rejects_a_list(api_user):
    tts = TTS(api_user)
    with pytest.raises(TypeError):
        tts.AddDestination(["+64211234567", "+64211234568"])


def test_add_keypads_accepts_a_list_of_keypad_dicts(api_user):
    via_singular = TTS(api_user)
    via_singular.AddKeypad(Tone=1, RouteNumber="+6491234567")
    via_singular.AddKeypad(Tone=2, Play="You pressed 2")

    via_plural = TTS(api_user)
    result = via_plural.AddKeypads([
        {"Tone": 1, "RouteNumber": "+6491234567"},
        {"Tone": 2, "Play": "You pressed 2"},
    ])

    assert result is via_plural
    assert via_plural.Keypads == via_singular.Keypads


def test_add_keypads_accepts_a_tuple(api_user):
    via_singular = TTS(api_user)
    via_singular.AddKeypad(Tone=1, RouteNumber="+6491234567")
    via_singular.AddKeypad(Tone=2, Play="You pressed 2")

    via_plural = TTS(api_user)
    result = via_plural.AddKeypads((
        {"Tone": 1, "RouteNumber": "+6491234567"},
        {"Tone": 2, "Play": "You pressed 2"},
    ))

    assert result is via_plural
    assert via_plural.Keypads == via_singular.Keypads


def test_add_keypads_rejects_a_bare_string(api_user):
    tts = TTS(api_user)
    with pytest.raises(TypeError):
        tts.AddKeypads("not-a-list")


def test_add_keypads_rejects_a_dict(api_user):
    tts = TTS(api_user)
    with pytest.raises(TypeError):
        tts.AddKeypads({"Tone": 1, "RouteNumber": "+6491234567"})


def test_send_message_rejects_unknown_kwarg(api_user):
    tts = TTS(api_user)
    result = tts.SendMessage(Bogus="x", MessageToPeople="hi", Destination="+64211234567")

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


def test_send_message_rejects_missing_destination(api_user):
    tts = TTS(api_user)
    result = tts.SendMessage(MessageToPeople="hi")

    assert result.Result == "Failed"
    assert "Destinations" in result.ErrorMessage[0]


def test_send_message_rejects_missing_message(api_user):
    tts = TTS(api_user)
    result = tts.SendMessage(Destination="+64211234567")

    assert result.Result == "Failed"
    assert "MessageToPeople" in result.ErrorMessage[0]


@responses_lib.activate
def test_send_message_returns_message_id_on_200_with_no_result_field(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/tts",
        json={"MessageID": "msg-001"},
        status=200,
    )

    tts = TTS(api_user)
    result = tts.SendMessage(MessageToPeople="Hi", Destination="+64211234567")

    assert result.Result == "Success"
    assert result.MessageID == "msg-001"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["MessageToPeople"] == "Hi"


@responses_lib.activate
def test_send_message_401_maps_to_unauthorized(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/tts",
        json={"ErrorMessage": ["Access denied: Auth Token or credentials are incorrect or have expired."]},
        status=401,
    )

    tts = TTS(api_user)
    result = tts.SendMessage(MessageToPeople="Hi", Destination="+64211234567")

    assert result.Result == "Unauthorized"


@responses_lib.activate
def test_status_returns_message_detail_with_recipients(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/tts/msg-001",
        json={
            "MessageID": "msg-001",
            "JobStatus": "Completed",
            "Recipients": [
                {"Type": "Voice", "DestSeq": "00000001", "Destination": "+64211234567", "Status": "Success", "Result": "Answered"}
            ],
        },
        status=200,
    )

    tts = TTS(api_user)
    result = tts.Status("msg-001")

    assert result.Result == "Success"
    assert result.Recipients[0]["Result"] == "Answered"


@responses_lib.activate
def test_status_404_maps_to_record_not_found(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/tts/missing-id",
        json={"ErrorMessage": ["Message not found."]},
        status=404,
    )

    tts = TTS(api_user)
    result = tts.Status("missing-id")

    assert result.Result == "RecordNotFound"


@responses_lib.activate
def test_reschedule_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/tts/msg-001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Delayed", "Action": "Reschedule"},
        status=200,
    )

    tts = TTS(api_user)
    result = tts.Reschedule("msg-001", "2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert result.Action == "Reschedule"


@responses_lib.activate
def test_reschedule_escapes_message_id_in_path(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/tts/msg%2F001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg/001", "Status": "Delayed", "Action": "Reschedule"},
        status=200,
    )

    tts = TTS(api_user)
    result = tts.Reschedule("msg/001", "2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert responses_lib.calls[0].request.url == "https://api.tnz.co.nz/api/v3.00/tts/msg%2F001/reschedule"


@responses_lib.activate
def test_abort_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/tts/msg-001/abort",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Completed", "Action": "Abort"},
        status=200,
    )

    tts = TTS(api_user)
    result = tts.Abort("msg-001")

    assert result.Result == "Success"
    assert result.Action == "Abort"


@responses_lib.activate
def test_resubmit_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/tts/msg-001/resubmit",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Pending", "Action": "Resubmit"},
        status=200,
    )

    tts = TTS(api_user)
    result = tts.Resubmit("msg-001", "2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert result.Action == "Resubmit"


def test_resubmit_raises_when_message_id_is_none(api_user):
    tts = TTS(api_user)

    with pytest.raises(ValueError, match="MessageID"):
        tts.Resubmit(None, "2026-08-01T09:00:00")


@responses_lib.activate
def test_pacing_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/tts/msg-001/pacing",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Pending", "Action": "Pacing"},
        status=200,
    )

    tts = TTS(api_user)
    result = tts.Pacing("msg-001", 10)

    assert result.Result == "Success"
    assert result.Action == "Pacing"
    assert json.loads(responses_lib.calls[0].request.body) == {"NumberOfOperators": 10}


def test_pacing_raises_when_message_id_is_empty(api_user):
    tts = TTS(api_user)

    with pytest.raises(ValueError, match="MessageID"):
        tts.Pacing("", 10)


def test_set_applies_multiple_fields_and_returns_self(api_user):
    tts = TTS(api_user)
    returned = tts.Set(MessageToPeople="Hi", Reference="Test")

    assert returned is tts
    assert tts.MessageToPeople == "Hi"
    assert tts.Reference == "Test"


def test_set_raises_on_unknown_field(api_user):
    tts = TTS(api_user)
    with pytest.raises(ValueError):
        tts.Set(Bogus="x")


def test_add_destination_with_string_wraps_as_to_number(api_user):
    tts = TTS(api_user)
    tts.AddDestination("+64211234567")

    assert tts.Destinations == [{"ToNumber": "+64211234567"}]


def test_add_destination_with_dict_appends_as_is(api_user):
    tts = TTS(api_user)
    tts.AddDestination({"ToNumber": "+64211234567", "FirstName": "Alice"})

    assert tts.Destinations == [{"ToNumber": "+64211234567", "FirstName": "Alice"}]


def test_add_destinations_with_mixed_list_adds_each_item(api_user):
    tts = TTS(api_user)
    tts.AddDestinations(["+64211234567", {"ToNumber": "+64221234567", "FirstName": "Bob"}])

    assert tts.Destinations == [{"ToNumber": "+64211234567"}, {"ToNumber": "+64221234567", "FirstName": "Bob"}]


def test_add_destination_with_contact_id(api_user):
    tts = TTS(api_user)
    tts.AddDestination(contact_id="6000000b-f002-4007-b00a-c00000000001")

    assert tts.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_destination_with_group_id(api_user):
    tts = TTS(api_user)
    tts.AddDestination(group_id="4000000b-f002-4007-b00a-c00000000002")

    assert tts.Destinations == [{"GroupID": "4000000b-f002-4007-b00a-c00000000002"}]


def test_add_destination_rejects_unknown_dict_key(api_user):
    tts = TTS(api_user)
    with pytest.raises(ValueError, match="ToNunber"):
        tts.AddDestination({"ToNunber": "+64211234567"})


def test_add_destination_accepts_a_destination_instance(api_user):
    tts = TTS(api_user)
    tts.AddDestination(Destination(ToNumber="+64211234567"))

    assert tts.Destinations == [{"ToNumber": "+64211234567"}]


def test_add_destination_accepts_main_phone(api_user):
    tts = TTS(api_user)
    tts.AddDestination({"MainPhone": "+64211234567"})

    assert tts.Destinations == [{"MainPhone": "+64211234567"}]


def test_send_message_rejects_destination_with_unknown_key(api_user):
    tts = TTS(api_user)
    result = tts.SendMessage(MessageToPeople="Hi", Destinations=[{"ToNunber": "+64211234567"}])

    assert result.Result == "Failed"
    assert "ToNunber" in result.ErrorMessage[0]


def test_add_destination_chains(api_user):
    tts = TTS(api_user)
    result = tts.AddDestination("+64211234567").AddDestination("+64221234567")

    assert result is tts
    assert len(tts.Destinations) == 2


def test_add_keypad_appends_full_fields(api_user):
    tts = TTS(api_user)
    tts.AddKeypad(tone=1, play="You pressed 1", route_number="+6491234567", play_section="Main")

    assert tts.Keypads == [{"Tone": 1, "Play": "You pressed 1", "RouteNumber": "+6491234567", "PlaySection": "Main"}]


def test_add_keypad_omits_none_optional_fields(api_user):
    tts = TTS(api_user)
    tts.AddKeypad(tone=2)

    assert tts.Keypads == [{"Tone": 2}]


def test_add_keypad_chains(api_user):
    tts = TTS(api_user)
    result = tts.AddKeypad(tone=1).AddKeypad(tone=2)

    assert result is tts
    assert len(tts.Keypads) == 2


def test_build_returns_independent_copy(api_user):
    tts = TTS(api_user)
    tts.MessageToPeople = "Hi"
    tts.AddDestination("+64211234567")

    model = tts.Build()

    assert model.MessageToPeople == "Hi"
    assert model.Destinations == [{"ToNumber": "+64211234567"}]

    # mutating the builder after Build() must not affect the already-returned model
    tts.AddDestination("+64221234567")
    assert len(model.Destinations) == 1
    assert len(tts.Destinations) == 2

    # mutating a destination dict already captured by Build() must not leak through either
    tts.Destinations[0]["ToNumber"] = "+64299999999"
    assert model.Destinations[0]["ToNumber"] == "+64211234567"


@responses_lib.activate
def test_send_message_accepts_prebuilt_model(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/tts",
        json={"MessageID": "msg-010"},
        status=200,
    )

    builder = TTS(api_user)
    model = builder.Set(MessageToPeople="From model").AddDestination("+64211234567").Build()

    tts = TTS(api_user)
    result = tts.SendMessage(model)

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["MessageToPeople"] == "From model"
    assert sent_body["Destinations"] == [{"ToNumber": "+64211234567"}]


@responses_lib.activate
def test_send_message_accepts_prebuilt_dict(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/tts",
        json={"MessageID": "msg-011"},
        status=200,
    )

    tts = TTS(api_user)
    result = tts.SendMessage({"MessageToPeople": "From dict", "Destinations": [{"ToNumber": "+64211234567"}]})

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["MessageToPeople"] == "From dict"


def test_send_message_rejects_invalid_model_type(api_user):
    tts = TTS(api_user)
    result = tts.SendMessage(model=12345)

    assert result.Result == "Failed"
    assert "12345" in result.ErrorMessage[0] or "int" in result.ErrorMessage[0]


def test_send_message_rejects_dict_model_with_unknown_key(api_user):
    tts = TTS(api_user)
    result = tts.SendMessage({"Bogus": "x"})

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


@responses_lib.activate
def test_send_message_dict_model_does_not_inherit_residual_set_state(api_user):
    tts = TTS(api_user)
    tts.Set(Reference="stale reference from a prior builder call")

    mock_endpoint(
        responses_lib.POST,
        "/tts",
        json={"MessageID": "msg-013"},
        status=200,
    )

    result = tts.SendMessage({"MessageToPeople": "Fresh message", "Destinations": [{"ToNumber": "+64211234567"}]})

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert "Reference" not in sent_body


@responses_lib.activate
def test_send_message_model_plus_kwargs_kwargs_supplement_model(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/tts",
        json={"MessageID": "msg-012"},
        status=200,
    )

    model = TTS(api_user).Set(MessageToPeople="Base").AddDestination("+64211234567").Build()

    tts = TTS(api_user)
    result = tts.SendMessage(model, Reference="Added on top")

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["MessageToPeople"] == "Base"
    assert sent_body["Reference"] == "Added on top"


@responses_lib.activate
def test_send_message_kwargs_only_still_works_unchanged(api_user):
    # Regression guard: the pre-existing kwargs-only call style must be completely unaffected.
    mock_endpoint(
        responses_lib.POST,
        "/tts",
        json={"MessageID": "msg-013"},
        status=200,
    )

    tts = TTS(api_user)
    result = tts.SendMessage(MessageToPeople="Old style", Destination="+64211234567")

    assert result.Result == "Success"

@responses_lib.activate
def test_status_accepts_new_pascalcase_kwarg(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/tts/msg-001",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    tts = TTS(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            tts.Status(MessageID="msg-001")
        except TypeError as exc:
            pytest.fail(f"MessageID kwarg not accepted: {exc}")


@responses_lib.activate
def test_status_old_snake_case_kwarg_still_works_with_warning(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/tts/msg-001",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    tts = TTS(api_user)
    with pytest.warns(DeprecationWarning, match="message_id"):
        tts.Status(message_id="msg-001")


@responses_lib.activate
def test_reschedule_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/tts/msg-001/reschedule",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    tts = TTS(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            tts.Reschedule(MessageID="msg-001", SendTime="2026-08-01T09:00:00")
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_resubmit_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/tts/msg-001/resubmit",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    tts = TTS(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            tts.Resubmit(MessageID="msg-001", SendTime="2026-08-01T09:00:00")
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_pacing_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/tts/msg-001/pacing",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    tts = TTS(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            tts.Pacing(MessageID="msg-001", NumberOfOperators=10)
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_pacing_old_snake_case_kwargs_still_work_with_warning(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/tts/msg-001/pacing",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    tts = TTS(api_user)
    with pytest.warns(DeprecationWarning):
        tts.Pacing(message_id="msg-001", number_of_operators=10)


def test_add_destination_new_pascalcase_kwargs_accepted(api_user):
    tts = TTS(api_user)
    tts.AddDestination(ContactID="6000000b-f002-4007-b00a-c00000000001")
    assert tts.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_destination_old_snake_case_kwarg_still_works_with_warning(api_user):
    tts = TTS(api_user)
    with pytest.warns(DeprecationWarning, match="contact_id"):
        tts.AddDestination(contact_id="6000000b-f002-4007-b00a-c00000000001")
    assert tts.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_keypad_new_pascalcase_kwargs_accepted(api_user):
    tts = TTS(api_user)
    tts.AddKeypad(Tone=1, Play="You pressed 1", RouteNumber="+6491232345", PlaySection="Main")
    assert tts.Keypads == [{"Tone": 1, "Play": "You pressed 1", "RouteNumber": "+6491232345", "PlaySection": "Main"}]


def test_add_keypad_old_snake_case_kwargs_still_work_with_warning(api_user):
    tts = TTS(api_user)
    with pytest.warns(DeprecationWarning):
        tts.AddKeypad(tone=1, play="You pressed 1", route_number="+6491232345", play_section="Main")
    assert tts.Keypads == [{"Tone": 1, "Play": "You pressed 1", "RouteNumber": "+6491232345", "PlaySection": "Main"}]


def test_old_tts_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="TTSResponseDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.tts_response import TTSResponseDTO

    from tnzapi.api.v300.messaging.models.responses.tts_response import TTSResponse
    assert TTSResponseDTO is TTSResponse


def test_old_tts_status_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="TTSStatusDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.tts_status import TTSStatusDTO

    from tnzapi.api.v300.messaging.models.responses.tts_status import TTSStatus
    assert TTSStatusDTO is TTSStatus


def test_old_tts_action_result_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="TTSActionResultDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.tts_action_result import TTSActionResultDTO

    from tnzapi.api.v300.messaging.models.responses.tts_action_result import TTSActionResult
    assert TTSActionResultDTO is TTSActionResult


def test_old_tts_request_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="TTSRequestDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.requests.tts_request import TTSRequestDTO

    from tnzapi.api.v300.messaging.models.requests.tts_request import TTSRequest
    assert TTSRequestDTO is TTSRequest


def test_message_to_people_is_never_path_detected_or_warned(tmp_path, api_user, recwarn):
    """TTS's MessageToPeople is spoken text, never base64 audio - unlike Voice's
    same-named field, an existing file path here must be stored literally,
    unchanged, with no file read and no warning."""
    path = tmp_path / "not-audio.wav"
    path.write_bytes(b"this must never be read")
    tts = TTS(api_user)

    tts.Set(MessageToPeople=str(path))

    assert tts.MessageToPeople == str(path)
    assert len(recwarn) == 0
