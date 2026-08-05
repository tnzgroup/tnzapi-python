import json
import warnings

import pytest
import responses as responses_lib

from tnzapi.api.v300.actions.builders.pacing import Pacing
from tests.conftest import mock_endpoint


def test_send_request_rejects_sms_not_supported(api_user):
    pacing = Pacing(api_user)
    result = pacing.SendRequest(channel="sms", message_id="msg-001", number_of_operators=5)

    assert result.Result == "Failed"
    assert "sms" in result.ErrorMessage[0].lower()


def test_send_request_rejects_email_not_supported(api_user):
    pacing = Pacing(api_user)
    result = pacing.SendRequest(channel="email", message_id="msg-001", number_of_operators=5)

    assert result.Result == "Failed"


def test_send_request_rejects_unknown_channel(api_user):
    pacing = Pacing(api_user)
    result = pacing.SendRequest(channel="workflow", message_id="msg-001", number_of_operators=5)

    assert result.Result == "Failed"


@responses_lib.activate
def test_send_request_dispatches_to_tts_pacing(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/tts/msg-001/pacing",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Pending", "Action": "Pacing"},
        status=200,
    )

    pacing = Pacing(api_user)
    result = pacing.SendRequest(channel="tts", message_id="msg-001", number_of_operators=10)

    assert result.Result == "Success"
    assert json.loads(responses_lib.calls[0].request.body) == {"NumberOfOperators": 10}


@responses_lib.activate
def test_send_request_dispatches_to_voice_pacing(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/voice/msg-002/pacing",
        json={"ActionResult": "Success", "MessageID": "msg-002", "Status": "Pending", "Action": "Pacing"},
        status=200,
    )

    pacing = Pacing(api_user)
    result = pacing.SendRequest(channel="voice", message_id="msg-002", number_of_operators=3)

    assert result.Result == "Success"
    assert json.loads(responses_lib.calls[0].request.body) == {"NumberOfOperators": 3}


@responses_lib.activate
def test_send_request_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/tts/ID123456/pacing",
        json={"ActionResult": "Success", "MessageID": "ID123456", "Status": "Pending", "Action": "Pacing"},
        status=200,
    )

    pacing = Pacing(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            pacing.SendRequest(Channel="tts", MessageID="ID123456", NumberOfOperators=10)
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_send_request_old_snake_case_kwargs_still_work_with_warning(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/tts/ID123456/pacing",
        json={"ActionResult": "Success", "MessageID": "ID123456", "Status": "Pending", "Action": "Pacing"},
        status=200,
    )

    pacing = Pacing(api_user)
    with pytest.warns(DeprecationWarning):
        pacing.SendRequest(channel="tts", message_id="ID123456", number_of_operators=10)
