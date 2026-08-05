import json
import warnings

import pytest
import responses as responses_lib

from tnzapi.api.v300.actions.builders.reschedule import Reschedule
from tests.conftest import mock_endpoint


def test_send_request_rejects_unknown_channel(api_user):
    reschedule = Reschedule(api_user)
    result = reschedule.SendRequest(channel="workflow", message_id="msg-001", send_time="2026-08-01T09:00:00")

    assert result.Result == "Failed"


@responses_lib.activate
def test_send_request_dispatches_to_tts_reschedule(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/tts/msg-001/reschedule",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Delayed", "Action": "Reschedule"},
        status=200,
    )

    reschedule = Reschedule(api_user)
    result = reschedule.SendRequest(channel="tts", message_id="msg-001", send_time="2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert json.loads(responses_lib.calls[0].request.body) == {"SendTime": "2026-08-01T09:00:00"}


@responses_lib.activate
def test_send_request_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/sms/ID123456/reschedule",
        json={"ActionResult": "Success", "MessageID": "ID123456", "Status": "Delayed", "Action": "Reschedule"},
        status=200,
    )

    reschedule = Reschedule(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            reschedule.SendRequest(Channel="sms", MessageID="ID123456", SendTime="2026-08-01T09:00:00")
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_send_request_old_snake_case_kwargs_still_work_with_warning(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/sms/ID123456/reschedule",
        json={"ActionResult": "Success", "MessageID": "ID123456", "Status": "Delayed", "Action": "Reschedule"},
        status=200,
    )

    reschedule = Reschedule(api_user)
    with pytest.warns(DeprecationWarning):
        reschedule.SendRequest(channel="sms", message_id="ID123456", send_time="2026-08-01T09:00:00")
