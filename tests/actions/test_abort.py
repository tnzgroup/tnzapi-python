import warnings

import pytest
import responses as responses_lib

from tnzapi.api.v300.actions.builders.abort import Abort
from tests.conftest import mock_endpoint


def test_send_request_rejects_unknown_channel(api_user):
    abort = Abort(api_user)
    result = abort.SendRequest(channel="workflow", message_id="msg-001")

    assert result.Result == "Failed"
    assert "workflow" in result.ErrorMessage[0].lower()


@responses_lib.activate
def test_send_request_dispatches_to_sms_abort(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/sms/msg-001/abort",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Completed", "Action": "Abort"},
        status=200,
    )

    abort = Abort(api_user)
    result = abort.SendRequest(channel="sms", message_id="msg-001")

    assert result.Result == "Success"
    assert result.Action == "Abort"


@responses_lib.activate
def test_send_request_dispatches_to_rcs_abort(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/rcs/msg-002/abort",
        json={"ActionResult": "Success", "MessageID": "msg-002", "Status": "Completed", "Action": "Abort"},
        status=200,
    )

    abort = Abort(api_user)
    result = abort.SendRequest(channel="rcs", message_id="msg-002")

    assert result.Result == "Success"
    assert result.Action == "Abort"


@responses_lib.activate
def test_send_request_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/sms/ID123456/abort",
        json={"ActionResult": "Success", "MessageID": "ID123456", "Status": "Completed", "Action": "Abort"},
        status=200,
    )

    abort = Abort(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            abort.SendRequest(Channel="sms", MessageID="ID123456")
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_send_request_old_snake_case_kwargs_still_work_with_warning(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/sms/ID123456/abort",
        json={"ActionResult": "Success", "MessageID": "ID123456", "Status": "Completed", "Action": "Abort"},
        status=200,
    )

    abort = Abort(api_user)
    with pytest.warns(DeprecationWarning):
        abort.SendRequest(channel="sms", message_id="ID123456")


def test_old_action_error_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="ActionErrorDTO is deprecated"):
        from tnzapi.api.v300.actions.models.responses.action_error import ActionErrorDTO

    from tnzapi.api.v300.actions.models.responses.action_error import ActionError
    assert ActionErrorDTO is ActionError
