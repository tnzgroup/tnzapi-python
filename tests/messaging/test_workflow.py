import json
import warnings

import pytest
import responses as responses_lib

from tnzapi.api.v300.messaging.builders.workflow import Workflow
from tnzapi.core.destination import Destination
from tests.conftest import mock_endpoint


def test_send_message_builds_correct_request_body(api_user):
    workflow = Workflow(api_user)
    workflow.WorkflowTemplateID = "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    workflow.Destinations = [{"ToNumber": "+64211234567", "EmailAddress": "john.doe@example.com"}]

    body = workflow._build_request_body()

    assert body["WorkflowTemplateID"] == "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    assert body["Destinations"] == [{"ToNumber": "+64211234567", "EmailAddress": "john.doe@example.com"}]


def test_add_destinations_loops_over_items_calling_add_destination(api_user):
    via_singular = Workflow(api_user)
    via_singular.AddDestination("+64211234567")
    via_singular.AddDestination("+64211234568")

    via_plural = Workflow(api_user)
    result = via_plural.AddDestinations(["+64211234567", "+64211234568"])

    assert result is via_plural
    assert via_plural.Destinations == via_singular.Destinations


def test_add_destinations_accepts_a_tuple(api_user):
    via_singular = Workflow(api_user)
    via_singular.AddDestination("+64211234567")
    via_singular.AddDestination("+64211234568")

    via_plural = Workflow(api_user)
    result = via_plural.AddDestinations(("+64211234567", "+64211234568"))

    assert result is via_plural
    assert via_plural.Destinations == via_singular.Destinations


def test_add_destinations_rejects_a_bare_string(api_user):
    workflow = Workflow(api_user)
    with pytest.raises(TypeError):
        workflow.AddDestinations("+64211234567")


def test_add_destinations_rejects_a_dict(api_user):
    workflow = Workflow(api_user)
    with pytest.raises(TypeError):
        workflow.AddDestinations({"ToNumber": "+64211234567"})


def test_add_destination_rejects_a_list(api_user):
    workflow = Workflow(api_user)
    with pytest.raises(TypeError):
        workflow.AddDestination(["+64211234567", "+64211234568"])


def test_send_message_rejects_unknown_kwarg(api_user):
    workflow = Workflow(api_user)
    result = workflow.SendMessage(Bogus="x", WorkflowTemplateID="a1b2c3d4-e5f6-7890-1234-567890abcdef", Destination="+64211234567")

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


def test_send_message_rejects_missing_destination(api_user):
    workflow = Workflow(api_user)
    result = workflow.SendMessage(WorkflowTemplateID="a1b2c3d4-e5f6-7890-1234-567890abcdef")

    assert result.Result == "Failed"
    assert "Destinations" in result.ErrorMessage[0]


def test_send_message_rejects_contact_id_alone_as_destination(api_user):
    # Unlike every other channel, ContactID/GroupID/MainPhone alone do NOT satisfy
    # Workflow's destination check - only Destinations/Destination/ToNumber do.
    workflow = Workflow(api_user)
    result = workflow.SendMessage(
        WorkflowTemplateID="a1b2c3d4-e5f6-7890-1234-567890abcdef",
        ContactID="c-001",
    )

    assert result.Result == "Failed"
    assert "Destinations" in result.ErrorMessage[0]


@responses_lib.activate
def test_send_message_accepts_a_destination(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/workflow",
        json={"MessageID": "msg-001"},
        status=200,
    )

    workflow = Workflow(api_user)
    result = workflow.SendMessage(
        WorkflowTemplateID="a1b2c3d4-e5f6-7890-1234-567890abcdef",
        Destination="+64211234567",
    )

    assert result.Result == "Success"


def test_send_message_rejects_missing_workflow_template_id(api_user):
    workflow = Workflow(api_user)
    result = workflow.SendMessage(Destination="+64211234567")

    assert result.Result == "Failed"
    assert "WorkflowTemplateID" in result.ErrorMessage[0]


def test_workflow_has_no_lifecycle_action_methods(api_user):
    workflow = Workflow(api_user)
    for method_name in ("Status", "Reschedule", "Abort", "Resubmit", "Pacing", "Received"):
        assert not hasattr(Workflow, method_name), f"Workflow must not define {method_name} - no such endpoint exists"


def test_send_message_resets_state_even_if_http_post_raises(api_user, monkeypatch):
    workflow = Workflow(api_user)

    def _raise(*args, **kwargs):
        raise ConnectionError("network unreachable")

    monkeypatch.setattr(workflow.http, "post", _raise)

    with pytest.raises(ConnectionError):
        workflow.SendMessage(WorkflowTemplateID="a1b2c3d4-e5f6-7890-1234-567890abcdef", Destination="+64211234567")

    # _data must have been reset in the finally block, not left stale from the failed call
    assert workflow._data.WorkflowTemplateID is None
    assert workflow._data.Destination is None


def test_send_message_rejects_dunder_kwarg_instead_of_corrupting_data(api_user):
    workflow = Workflow(api_user)
    result = workflow.SendMessage(
        **{"__dict__": {}}, WorkflowTemplateID="a1b2c3d4-e5f6-7890-1234-567890abcdef", Destination="+64211234567"
    )

    assert result.Result == "Failed"
    assert "__dict__" in result.ErrorMessage[0]
    # a real dataclass field must still be settable afterwards - _data was not corrupted
    workflow.WorkflowTemplateID = "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    assert workflow.WorkflowTemplateID == "a1b2c3d4-e5f6-7890-1234-567890abcdef"


@responses_lib.activate
def test_send_message_returns_message_id_on_200_with_no_result_field(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/workflow",
        json={"MessageID": "msg-001"},
        status=200,
    )

    workflow = Workflow(api_user)
    result = workflow.SendMessage(
        WorkflowTemplateID="a1b2c3d4-e5f6-7890-1234-567890abcdef", Destination="+64211234567"
    )

    assert result.Result == "Success"
    assert result.MessageID == "msg-001"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["WorkflowTemplateID"] == "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    assert sent_body["Destination"] == "+64211234567"


@responses_lib.activate
def test_send_message_401_maps_to_unauthorized(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/workflow",
        json={"ErrorMessage": ["Access denied: Auth Token or credentials are incorrect or have expired."]},
        status=401,
    )

    workflow = Workflow(api_user)
    result = workflow.SendMessage(
        WorkflowTemplateID="a1b2c3d4-e5f6-7890-1234-567890abcdef", Destination="+64211234567"
    )

    assert result.Result == "Unauthorized"


@responses_lib.activate
def test_send_message_omni_channel_destination_round_trips(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/workflow",
        json={"MessageID": "msg-002"},
        status=200,
    )

    workflow = Workflow(api_user)
    result = workflow.SendMessage(
        WorkflowTemplateID="a1b2c3d4-e5f6-7890-1234-567890abcdef",
        Destinations=[
            {
                "ToNumber": "+64211234567",
                "MainPhone": "+6495005000",
                "EmailAddress": "john.doe@example.com",
                "FirstName": "John",
                "LastName": "Doe",
            }
        ],
    )

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    destination = sent_body["Destinations"][0]
    assert destination["ToNumber"] == "+64211234567"
    assert destination["MainPhone"] == "+6495005000"
    assert destination["EmailAddress"] == "john.doe@example.com"


def test_set_applies_multiple_fields_and_returns_self(api_user):
    workflow = Workflow(api_user)
    returned = workflow.Set(WorkflowTemplateID="a1b2c3d4-e5f6-7890-1234-567890abcdef", Reference="Test")

    assert returned is workflow
    assert workflow.WorkflowTemplateID == "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    assert workflow.Reference == "Test"


def test_set_raises_on_unknown_field(api_user):
    workflow = Workflow(api_user)
    with pytest.raises(ValueError):
        workflow.Set(Bogus="x")


def test_add_destination_with_string_wraps_as_to_number(api_user):
    workflow = Workflow(api_user)
    workflow.AddDestination("+64211234567")

    assert workflow.Destinations == [{"ToNumber": "+64211234567"}]


def test_add_destination_with_dict_appends_as_is(api_user):
    workflow = Workflow(api_user)
    workflow.AddDestination({"ToNumber": "+64211234567", "FirstName": "Alice"})

    assert workflow.Destinations == [{"ToNumber": "+64211234567", "FirstName": "Alice"}]


def test_add_destination_supports_omni_channel_dict(api_user):
    workflow = Workflow(api_user)
    workflow.AddDestination({"ToNumber": "+64211234567", "MainPhone": "+6495005000", "EmailAddress": "john.doe@example.com"})

    assert workflow.Destinations == [{"ToNumber": "+64211234567", "MainPhone": "+6495005000", "EmailAddress": "john.doe@example.com"}]


def test_add_destinations_with_mixed_list_adds_each_item(api_user):
    workflow = Workflow(api_user)
    workflow.AddDestinations(["+64211234567", {"ToNumber": "+64221234567", "FirstName": "Bob"}])

    assert workflow.Destinations == [{"ToNumber": "+64211234567"}, {"ToNumber": "+64221234567", "FirstName": "Bob"}]


def test_add_destination_with_contact_id(api_user):
    workflow = Workflow(api_user)
    workflow.AddDestination(contact_id="6000000b-f002-4007-b00a-c00000000001")

    assert workflow.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_destination_with_group_id(api_user):
    workflow = Workflow(api_user)
    workflow.AddDestination(group_id="4000000b-f002-4007-b00a-c00000000002")

    assert workflow.Destinations == [{"GroupID": "4000000b-f002-4007-b00a-c00000000002"}]


def test_add_destination_rejects_unknown_dict_key(api_user):
    workflow = Workflow(api_user)
    with pytest.raises(ValueError, match="ToNunber"):
        workflow.AddDestination({"ToNunber": "+64211234567"})


def test_add_destination_accepts_a_destination_instance(api_user):
    workflow = Workflow(api_user)
    workflow.AddDestination(Destination(ToNumber="+64211234567", EmailAddress="test@example.com"))

    assert workflow.Destinations == [{"ToNumber": "+64211234567", "EmailAddress": "test@example.com"}]


def test_add_destination_accepts_mobile_phone_and_main_phone_together(api_user):
    workflow = Workflow(api_user)
    workflow.AddDestination({"MobilePhone": "+64211234567", "MainPhone": "+6491234567"})

    assert workflow.Destinations == [{"MobilePhone": "+64211234567", "MainPhone": "+6491234567"}]


def test_send_message_rejects_destination_with_unknown_key(api_user):
    workflow = Workflow(api_user)
    result = workflow.SendMessage(
        WorkflowTemplateID="tmpl-1", Destinations=[{"ToNunber": "+64211234567"}]
    )

    assert result.Result == "Failed"
    assert "ToNunber" in result.ErrorMessage[0]


def test_add_destination_chains(api_user):
    workflow = Workflow(api_user)
    result = workflow.AddDestination("+64211234567").AddDestination("+64221234567")

    assert result is workflow
    assert len(workflow.Destinations) == 2


def test_workflow_has_no_attachment_or_keypad_methods(api_user):
    for method_name in ("AddAttachment", "AddKeypad"):
        assert not hasattr(Workflow, method_name), f"Workflow must not define {method_name} - no such field exists"


def test_build_returns_independent_copy(api_user):
    workflow = Workflow(api_user)
    workflow.WorkflowTemplateID = "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    workflow.AddDestination("+64211234567")

    model = workflow.Build()

    assert model.WorkflowTemplateID == "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    assert model.Destinations == [{"ToNumber": "+64211234567"}]

    # mutating the builder after Build() must not affect the already-returned model
    workflow.AddDestination("+64221234567")
    assert len(model.Destinations) == 1
    assert len(workflow.Destinations) == 2

    # mutating a destination dict already captured by Build() must not leak through either
    workflow.Destinations[0]["ToNumber"] = "+64299999999"
    assert model.Destinations[0]["ToNumber"] == "+64211234567"


@responses_lib.activate
def test_send_message_accepts_prebuilt_model(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/workflow",
        json={"MessageID": "msg-010"},
        status=200,
    )

    builder = Workflow(api_user)
    model = (
        builder.Set(WorkflowTemplateID="a1b2c3d4-e5f6-7890-1234-567890abcdef")
        .AddDestination("+64211234567")
        .Build()
    )

    workflow = Workflow(api_user)
    result = workflow.SendMessage(model)

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["WorkflowTemplateID"] == "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    assert sent_body["Destinations"] == [{"ToNumber": "+64211234567"}]


@responses_lib.activate
def test_send_message_accepts_prebuilt_dict(api_user):
    mock_endpoint(
        responses_lib.POST,
        "/workflow",
        json={"MessageID": "msg-011"},
        status=200,
    )

    workflow = Workflow(api_user)
    result = workflow.SendMessage(
        {
            "WorkflowTemplateID": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
            "Destinations": [{"ToNumber": "+64211234567"}],
        }
    )

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert sent_body["WorkflowTemplateID"] == "a1b2c3d4-e5f6-7890-1234-567890abcdef"


def test_send_message_rejects_invalid_model_type(api_user):
    workflow = Workflow(api_user)
    result = workflow.SendMessage(model=12345)

    assert result.Result == "Failed"
    assert "12345" in result.ErrorMessage[0] or "int" in result.ErrorMessage[0]


@responses_lib.activate
def test_send_message_dict_model_does_not_inherit_residual_set_state(api_user):
    workflow = Workflow(api_user)
    workflow.Set(Reference="stale reference from a prior builder call")

    mock_endpoint(
        responses_lib.POST,
        "/workflow",
        json={"MessageID": "msg-013"},
        status=200,
    )

    result = workflow.SendMessage(
        {
            "WorkflowTemplateID": "a1b2c3d4-e5f6-7890-1234-567890abcdef",
            "Destinations": [{"ToNumber": "+64211234567"}],
        }
    )

    assert result.Result == "Success"
    sent_body = json.loads(responses_lib.calls[0].request.body)
    assert "Reference" not in sent_body


def test_send_message_rejects_dict_model_with_unknown_key(api_user):
    workflow = Workflow(api_user)
    result = workflow.SendMessage({"Bogus": "x"})

    assert result.Result == "Failed"
    assert "Bogus" in result.ErrorMessage[0]


def test_send_message_model_still_enforces_workflow_template_id(api_user):
    model = Workflow(api_user).AddDestination("+64211234567").Build()  # missing WorkflowTemplateID

    workflow = Workflow(api_user)
    result = workflow.SendMessage(model)

    assert result.Result == "Failed"
    assert "WorkflowTemplateID" in result.ErrorMessage[0]


@responses_lib.activate
def test_send_message_kwargs_only_still_works_unchanged(api_user):
    # Regression guard: the pre-existing kwargs-only call style must be completely unaffected.
    mock_endpoint(
        responses_lib.POST,
        "/workflow",
        json={"MessageID": "msg-013"},
        status=200,
    )

    workflow = Workflow(api_user)
    result = workflow.SendMessage(
        WorkflowTemplateID="a1b2c3d4-e5f6-7890-1234-567890abcdef", Destination="+64211234567"
    )

    assert result.Result == "Success"


def test_add_destination_new_pascalcase_kwargs_accepted(api_user):
    workflow = Workflow(api_user)
    workflow.AddDestination(ContactID="6000000b-f002-4007-b00a-c00000000001")
    assert workflow.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_add_destination_old_snake_case_kwarg_still_works_with_warning(api_user):
    workflow = Workflow(api_user)
    with pytest.warns(DeprecationWarning, match="contact_id"):
        workflow.AddDestination(contact_id="6000000b-f002-4007-b00a-c00000000001")
    assert workflow.Destinations == [{"ContactID": "6000000b-f002-4007-b00a-c00000000001"}]


def test_old_workflow_response_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="WorkflowResponseDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.workflow_response import WorkflowResponseDTO

    from tnzapi.api.v300.messaging.models.responses.workflow_response import WorkflowResponse
    assert WorkflowResponseDTO is WorkflowResponse


def test_old_workflow_request_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="WorkflowRequestDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.requests.workflow_request import WorkflowRequestDTO

    from tnzapi.api.v300.messaging.models.requests.workflow_request import WorkflowRequest
    assert WorkflowRequestDTO is WorkflowRequest
