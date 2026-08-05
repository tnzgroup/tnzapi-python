import json
import warnings

import pytest
import responses as responses_lib

from tnzapi.api.v300.messaging.builders.voice import Voice
from tnzapi.core.auth import TNZApiUser
from tnzapi.core.destination import Destination
from tnzapi.core.file_attachment import FileAttachment
from tests.conftest import mock_endpoint


def test_send_message_builds_correct_request_body(api_user):
    voice = Voice(api_user)
    voice.MessageToPeople = "base64audiodata"
    voice.Destinations = [{"MainPhone": "+64211234567"}]

    body = voice._build_request_body()

    assert body["MessageToPeople"] == "base64audiodata"


def test_add_destinations_loops_over_items_calling_add_destination(api_user):
    via_singular = Voice(api_user)
    via_singular.AddDestination("+64211234567")
    via_singular.AddDestination("+64211234568")

    via_plural = Voice(api_user)
    result = via_plural.AddDestinations(["+64211234567", "+64211234568"])

    assert result is via_plural
    assert via_plural.Destinations == via_singular.Destinations


def test_add_destinations_accepts_a_tuple(api_user):
    via_singular = Voice(api_user)
    via_singular.AddDestination("+64211234567")
    via_singular.AddDestination("+64211234568")

    via_plural = Voice(api_user)
    result = via_plural.AddDestinations(("+64211234567", "+64211234568"))

    assert result is via_plural
    assert via_plural.Destinations == via_singular.Destinations


def test_add_destinations_rejects_a_bare_string(api_user):
    voice = Voice(api_user)
    with pytest.raises(TypeError):
        voice.AddDestinations("+64211234567")


def test_add_destinations_rejects_a_dict(api_user):
    voice = Voice(api_user)
    with pytest.raises(TypeError):
        voice.AddDestinations({"ToNumber": "+64211234567"})


def test_add_destination_rejects_a_list(api_user):
    voice = Voice(api_user)
    with pytest.raises(TypeError):
        voice.AddDestination(["+64211234567", "+64211234568"])


def test_add_keypads_accepts_a_list_of_keypad_dicts(api_user):
    via_singular = Voice(api_user)
    via_singular.AddKeypad(Tone=1, RouteNumber="+6491234567")
    via_singular.AddKeypad(Tone=2, PlaySection="Main")

    via_plural = Voice(api_user)
    result = via_plural.AddKeypads([
        {"Tone": 1, "RouteNumber": "+6491234567"},
        {"Tone": 2, "PlaySection": "Main"},
    ])

    assert result is via_plural
    assert via_plural.Keypads == via_singular.Keypads


def test_add_keypads_accepts_a_tuple(api_user):
    via_singular = Voice(api_user)
    via_singular.AddKeypad(Tone=1, RouteNumber="+6491234567")
    via_singular.AddKeypad(Tone=2, PlaySection="Main")

    via_plural = Voice(api_user)
    result = via_plural.AddKeypads((
        {"Tone": 1, "RouteNumber": "+6491234567"},
        {"Tone": 2, "PlaySection": "Main"},
    ))

    assert result is via_plural
    assert via_plural.Keypads == via_singular.Keypads


def test_add_keypads_rejects_a_bare_string(api_user):
    voice = Voice(api_user)
    with pytest.raises(TypeError):
        voice.AddKeypads("not-a-list")


def test_add_keypads_rejects_a_dict(api_user):
    voice = Voice(api_user)
    with pytest.raises(TypeError):
        voice.AddKeypads({"Tone": 1, "RouteNumber": "+6491234567"})


def test_send_message_rejects_unknown_kwarg(api_user):
    voice = Voice(api_user)
    result = voice.SendMessage(Bogus="x", MessageToPeople="audio", Destination="+64211234567")

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


def test_send_message_rejects_missing_destination(api_user):
    voice = Voice(api_user)
    result = voice.SendMessage(MessageToPeople="audio")

    assert result.Result == "Failed"
    assert "Destinations" in result.ErrorMessage[0]


def test_send_message_rejects_missing_message(api_user):
    voice = Voice(api_user)
    result = voice.SendMessage(Destination="+64211234567")

    assert result.Result == "Failed"
    assert "MessageToPeople" in result.ErrorMessage[0]


def test_no_voice_field_on_dto(api_user):
    voice = Voice(api_user)
    assert not hasattr(voice._data, "Voice")


@responses_lib.activate
def test_send_message_returns_message_id_on_200_with_no_result_field(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/voice",
        json={"MessageID": "msg-001"},
        status=200,
    )

    voice = Voice(api_user)
    result = voice.SendMessage(MessageToPeople="audio", Destination="+64211234567")

    assert result.Result == "Success"
    assert result.MessageID == "msg-001"


@responses_lib.activate
def test_send_message_401_maps_to_unauthorized(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/voice",
        json={"ErrorMessage": ["Access denied: Auth Token or credentials are incorrect or have expired."]},
        status=401,
    )

    voice = Voice(api_user)
    result = voice.SendMessage(MessageToPeople="audio", Destination="+64211234567")

    assert result.Result == "Unauthorized"


@responses_lib.activate
def test_status_returns_message_detail_with_recipients(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/voice/msg-001",
        json={"MessageID": "msg-001", "JobStatus": "Completed", "Recipients": []},
        status=200,
    )

    voice = Voice(api_user)
    result = voice.Status("msg-001")

    assert result.Result == "Success"


@responses_lib.activate
def test_status_404_maps_to_record_not_found(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/voice/missing-id",
        json={"ErrorMessage": ["Message not found."]},
        status=404,
    )

    voice = Voice(api_user)
    result = voice.Status("missing-id")

    assert result.Result == "RecordNotFound"


@responses_lib.activate
def test_reschedule_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/voice/msg-001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Delayed", "Action": "Reschedule"},
        status=200,
    )

    voice = Voice(api_user)
    result = voice.Reschedule("msg-001", "2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert result.Action == "Reschedule"


@responses_lib.activate
def test_reschedule_escapes_message_id_in_path(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/voice/msg%2F001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg/001", "Status": "Delayed", "Action": "Reschedule"},
        status=200,
    )

    voice = Voice(api_user)
    result = voice.Reschedule("msg/001", "2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert responses_lib.calls[0].request.url == "https://api.tnz.co.nz/api/v3.00/voice/msg%2F001/reschedule"


@responses_lib.activate
def test_abort_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/voice/msg-001/abort",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Completed", "Action": "Abort"},
        status=200,
    )

    voice = Voice(api_user)
    result = voice.Abort("msg-001")

    assert result.Result == "Success"
    assert result.Action == "Abort"


@responses_lib.activate
def test_resubmit_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/voice/msg-001/resubmit",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Pending", "Action": "Resubmit"},
        status=200,
    )

    voice = Voice(api_user)
    result = voice.Resubmit("msg-001", "2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert result.Action == "Resubmit"


@responses_lib.activate
def test_pacing_returns_action_result(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/voice/msg-001/pacing",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Pending", "Action": "Pacing"},
        status=200,
    )

    voice = Voice(api_user)
    result = voice.Pacing("msg-001", 5)

    assert result.Result == "Success"
    assert result.Action == "Pacing"


def test_set_applies_multiple_fields_and_returns_self(api_user):
    voice = Voice(api_user)
    returned = voice.Set(MessageToPeople="Hi", Reference="Test")

    assert returned is voice
    assert voice.MessageToPeople == "Hi"
    assert voice.Reference == "Test"


def test_set_raises_on_unknown_field(api_user):
    voice = Voice(api_user)
    with pytest.raises(ValueError):
        voice.Set(Bogus="x")


def test_add_destination_with_string_wraps_as_to_number(api_user):
    voice = Voice(api_user)
    voice.AddDestination("+64211234567")

    assert voice.Destinations == [{"ToNumber": "+64211234567"}]


def test_add_destination_with_dict_appends_as_is(api_user):
    voice = Voice(api_user)
    voice.AddDestination({"ToNumber": "+64211234567", "FirstName": "Alice"})

    assert voice.Destinations == [{"ToNumber": "+64211234567", "FirstName": "Alice"}]


def test_add_destinations_with_mixed_list_adds_each_item(api_user):
    voice = Voice(api_user)
    voice.AddDestinations(["+64211234567", {"ToNumber": "+64221234567", "FirstName": "Bob"}])

    assert voice.Destinations == [{"ToNumber": "+64211234567"}, {"ToNumber": "+64221234567", "FirstName": "Bob"}]


def test_add_destination_with_contact_id(api_user):
    voice = Voice(api_user)
    voice.AddDestination(contact_id="6000000b-f002-4007-b00a-c00000000001")

    assert voice.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_destination_with_group_id(api_user):
    voice = Voice(api_user)
    voice.AddDestination(group_id="4000000b-f002-4007-b00a-c00000000002")

    assert voice.Destinations == [{"GroupID": "4000000b-f002-4007-b00a-c00000000002"}]


def test_add_destination_rejects_unknown_dict_key(api_user):
    voice = Voice(api_user)
    with pytest.raises(ValueError, match="ToNunber"):
        voice.AddDestination({"ToNunber": "+64211234567"})


def test_add_destination_accepts_a_destination_instance(api_user):
    voice = Voice(api_user)
    voice.AddDestination(Destination(ToNumber="+64211234567"))

    assert voice.Destinations == [{"ToNumber": "+64211234567"}]


def test_add_destination_accepts_main_phone(api_user):
    voice = Voice(api_user)
    voice.AddDestination({"MainPhone": "+64211234567"})

    assert voice.Destinations == [{"MainPhone": "+64211234567"}]


def test_send_message_rejects_destination_with_unknown_key(api_user):
    voice = Voice(api_user)
    result = voice.SendMessage(MessageToPeople="base64audio==", Destinations=[{"ToNunber": "+64211234567"}])

    assert result.Result == "Failed"
    assert "ToNunber" in result.ErrorMessage[0]


def test_add_destination_chains(api_user):
    voice = Voice(api_user)
    result = voice.AddDestination("+64211234567").AddDestination("+64221234567")

    assert result is voice
    assert len(voice.Destinations) == 2


def test_add_keypad_appends_full_fields(api_user):
    voice = Voice(api_user)
    voice.AddKeypad(tone=1, play="base64audiodata", route_number="+6491234567", play_section="Main")

    assert voice.Keypads == [{"Tone": 1, "Play": "base64audiodata", "RouteNumber": "+6491234567", "PlaySection": "Main"}]


def test_message_to_people_real_path_resolves_with_no_warning(tmp_path, api_user, recwarn):
    path = tmp_path / "greeting.wav"
    path.write_bytes(b"audio-bytes")
    voice = Voice(api_user)

    voice.Set(MessageToPeople=str(path))

    import base64
    assert base64.b64decode(voice.MessageToPeople) == b"audio-bytes"
    assert len(recwarn) == 0


def test_message_to_people_non_path_string_passes_through_unchanged(api_user, recwarn):
    voice = Voice(api_user)

    voice.Set(MessageToPeople="literal-base64-audio==")

    assert voice.MessageToPeople == "literal-base64-audio=="
    assert len(recwarn) == 0


def test_message_to_people_file_attachment_instance_is_unwrapped_with_no_warning(api_user, recwarn):
    voice = Voice(api_user)
    attachment = FileAttachment(Name="greeting.wav", Data="already-resolved-base64==")

    voice.Set(MessageToPeople=attachment)

    assert voice.MessageToPeople == "already-resolved-base64=="
    assert len(recwarn) == 0


def test_call_route_message_to_operators_real_path_resolves(tmp_path, api_user, recwarn):
    path = tmp_path / "hold.wav"
    path.write_bytes(b"hold-audio")
    voice = Voice(api_user)

    voice.Set(CallRouteMessageToOperators=str(path))

    import base64
    assert base64.b64decode(voice.CallRouteMessageToOperators) == b"hold-audio"
    assert len(recwarn) == 0


def test_add_keypad_play_real_path_resolves_with_no_warning(tmp_path, api_user, recwarn):
    path = tmp_path / "key.wav"
    path.write_bytes(b"key-audio")
    voice = Voice(api_user)

    voice.AddKeypad(Tone=1, Play=str(path))

    import base64
    assert base64.b64decode(voice.Keypads[0]["Play"]) == b"key-audio"
    assert len(recwarn) == 0


def test_add_keypad_play_non_path_string_passes_through_unchanged(api_user, recwarn):
    voice = Voice(api_user)

    voice.AddKeypad(Tone=1, Play="literal-base64==")

    assert voice.Keypads[0]["Play"] == "literal-base64=="
    assert len(recwarn) == 0


def test_add_keypad_play_file_attachment_is_unwrapped_with_no_warning(api_user, recwarn):
    voice = Voice(api_user)
    attachment = FileAttachment(Name="key.wav", Data="already-resolved-base64==")

    voice.AddKeypad(Tone=1, Play=attachment)

    assert voice.Keypads[0]["Play"] == "already-resolved-base64=="
    assert len(recwarn) == 0


def test_add_keypad_omits_none_optional_fields(api_user):
    voice = Voice(api_user)
    voice.AddKeypad(tone=2)

    assert voice.Keypads == [{"Tone": 2}]


def test_add_keypad_chains(api_user):
    voice = Voice(api_user)
    result = voice.AddKeypad(tone=1).AddKeypad(tone=2)

    assert result is voice
    assert len(voice.Keypads) == 2


def test_build_returns_independent_copy(api_user):
    voice = Voice(api_user)
    voice.MessageToPeople = "audio"
    voice.AddDestination("+64211234567")

    model = voice.Build()

    assert model.MessageToPeople == "audio"
    assert model.Destinations == [{"ToNumber": "+64211234567"}]

    # mutating the builder after Build() must not affect the already-returned model
    voice.AddDestination("+64221234567")
    assert len(model.Destinations) == 1
    assert len(voice.Destinations) == 2

    # mutating a destination dict already captured by Build() must not leak through either
    voice.Destinations[0]["ToNumber"] = "+64299999999"
    assert model.Destinations[0]["ToNumber"] == "+64211234567"


@responses_lib.activate
def test_send_message_accepts_prebuilt_model(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/voice",
        json={"MessageID": "msg-010"},
        status=200,
    )

    builder = Voice(api_user)
    model = builder.Set(MessageToPeople="From model").AddDestination("+64211234567").Build()

    voice = Voice(api_user)
    result = voice.SendMessage(model)

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["MessageToPeople"] == "From model"
    assert sent_body["Destinations"] == [{"ToNumber": "+64211234567"}]


@responses_lib.activate
def test_send_message_accepts_prebuilt_dict(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/voice",
        json={"MessageID": "msg-011"},
        status=200,
    )

    voice = Voice(api_user)
    result = voice.SendMessage({"MessageToPeople": "From dict", "Destinations": [{"ToNumber": "+64211234567"}]})

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["MessageToPeople"] == "From dict"


def test_send_message_rejects_invalid_model_type(api_user):
    voice = Voice(api_user)
    result = voice.SendMessage(model=12345)

    assert result.Result == "Failed"
    assert "12345" in result.ErrorMessage[0] or "int" in result.ErrorMessage[0]


def test_send_message_rejects_dict_model_with_unknown_key(api_user):
    voice = Voice(api_user)
    result = voice.SendMessage({"Bogus": "x"})

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


@responses_lib.activate
def test_send_message_dict_model_does_not_inherit_residual_set_state(api_user):
    voice = Voice(api_user)
    voice.Set(Reference="stale reference from a prior builder call")

    mock_endpoint(
        responses_lib.POST,
        "/voice",
        json={"MessageID": "msg-013"},
        status=200,
    )

    result = voice.SendMessage({"MessageToPeople": "Fresh message", "Destinations": [{"ToNumber": "+64211234567"}]})

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert "Reference" not in sent_body


@responses_lib.activate
def test_send_message_model_plus_kwargs_kwargs_supplement_model(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/voice",
        json={"MessageID": "msg-012"},
        status=200,
    )

    model = Voice(api_user).Set(MessageToPeople="Base").AddDestination("+64211234567").Build()

    voice = Voice(api_user)
    result = voice.SendMessage(model, Reference="Added on top")

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["MessageToPeople"] == "Base"
    assert sent_body["Reference"] == "Added on top"


@responses_lib.activate
def test_send_message_kwargs_only_still_works_unchanged(api_user):
    # Regression guard: the pre-existing kwargs-only call style must be completely unaffected.
    mock_endpoint(
        responses_lib.POST,
        "/voice",
        json={"MessageID": "msg-013"},
        status=200,
    )

    voice = Voice(api_user)
    result = voice.SendMessage(MessageToPeople="Old style", Destination="+64211234567")

    assert result.Result == "Success"

@responses_lib.activate
def test_status_accepts_new_pascalcase_kwarg(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/voice/msg-001",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    voice = Voice(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            voice.Status(MessageID="msg-001")
        except TypeError as exc:
            pytest.fail(f"MessageID kwarg not accepted: {exc}")


@responses_lib.activate
def test_status_old_snake_case_kwarg_still_works_with_warning(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/voice/msg-001",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    voice = Voice(api_user)
    with pytest.warns(DeprecationWarning, match="message_id"):
        voice.Status(message_id="msg-001")


@responses_lib.activate
def test_reschedule_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/voice/msg-001/reschedule",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    voice = Voice(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            voice.Reschedule(MessageID="msg-001", SendTime="2026-08-01T09:00:00")
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_resubmit_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/voice/msg-001/resubmit",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    voice = Voice(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            voice.Resubmit(MessageID="msg-001", SendTime="2026-08-01T09:00:00")
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_pacing_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/voice/msg-001/pacing",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    voice = Voice(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            voice.Pacing(MessageID="msg-001", NumberOfOperators=10)
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_pacing_old_snake_case_kwargs_still_work_with_warning(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/voice/msg-001/pacing",
        json={"Result": "Success", "MessageID": "msg-001"},
        status=200,
    )

    voice = Voice(api_user)
    with pytest.warns(DeprecationWarning):
        voice.Pacing(message_id="msg-001", number_of_operators=10)


def test_add_destination_new_pascalcase_kwargs_accepted(api_user):
    voice = Voice(api_user)
    voice.AddDestination(ContactID="6000000b-f002-4007-b00a-c00000000001")
    assert voice.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_destination_old_snake_case_kwarg_still_works_with_warning(api_user):
    voice = Voice(api_user)
    with pytest.warns(DeprecationWarning, match="contact_id"):
        voice.AddDestination(contact_id="6000000b-f002-4007-b00a-c00000000001")
    assert voice.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_keypad_new_pascalcase_kwargs_accepted(api_user):
    voice = Voice(api_user)
    voice.AddKeypad(Tone=1, Play="base64audiodata", RouteNumber="+6491234567", PlaySection="Main")
    assert voice.Keypads == [{"Tone": 1, "Play": "base64audiodata", "RouteNumber": "+6491234567", "PlaySection": "Main"}]


def test_add_keypad_old_snake_case_kwargs_still_work_with_warning(api_user):
    voice = Voice(api_user)
    with pytest.warns(DeprecationWarning):
        voice.AddKeypad(tone=1, play="base64audiodata", route_number="+6491234567", play_section="Main")
    assert voice.Keypads == [{"Tone": 1, "Play": "base64audiodata", "RouteNumber": "+6491234567", "PlaySection": "Main"}]


def test_old_voice_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="VoiceResponseDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.voice_response import VoiceResponseDTO

    from tnzapi.api.v300.messaging.models.responses.voice_response import VoiceResponse
    assert VoiceResponseDTO is VoiceResponse


def test_old_voice_status_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="VoiceStatusDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.voice_status import VoiceStatusDTO

    from tnzapi.api.v300.messaging.models.responses.voice_status import VoiceStatus
    assert VoiceStatusDTO is VoiceStatus


def test_old_voice_action_result_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="VoiceActionResultDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.voice_action_result import VoiceActionResultDTO

    from tnzapi.api.v300.messaging.models.responses.voice_action_result import VoiceActionResult
    assert VoiceActionResultDTO is VoiceActionResult


def test_old_voice_request_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="VoiceRequestDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.requests.voice_request import VoiceRequestDTO

    from tnzapi.api.v300.messaging.models.requests.voice_request import VoiceRequest
    assert VoiceRequestDTO is VoiceRequest
