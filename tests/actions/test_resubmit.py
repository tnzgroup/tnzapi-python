import json
import warnings

import pytest
import responses as responses_lib

from tnzapi.api.v300.actions.builders.resubmit import Resubmit
from tests.conftest import mock_endpoint


def test_send_request_rejects_sms_not_supported(api_user):
    resubmit = Resubmit(api_user)
    result = resubmit.SendRequest(channel="sms", message_id="msg-001", send_time="2026-08-01T09:00:00")

    assert result.Result == "Failed"
    assert "sms" in result.ErrorMessage[0].lower()
    assert "resubmit" in result.ErrorMessage[0].lower()


def test_send_request_rejects_whatsapp_not_supported(api_user):
    resubmit = Resubmit(api_user)
    result = resubmit.SendRequest(channel="whatsapp", message_id="msg-001", send_time="2026-08-01T09:00:00")

    assert result.Result == "Failed"


def test_send_request_rejects_rcs_not_supported(api_user):
    resubmit = Resubmit(api_user)
    result = resubmit.SendRequest(channel="rcs", message_id="msg-001", send_time="2026-08-01T09:00:00")

    assert result.Result == "Failed"


def test_send_request_rejects_unknown_channel(api_user):
    resubmit = Resubmit(api_user)
    result = resubmit.SendRequest(channel="workflow", message_id="msg-001", send_time="2026-08-01T09:00:00")

    assert result.Result == "Failed"


@responses_lib.activate
def test_send_request_dispatches_to_email_resubmit(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/email/msg-001/resubmit",
        json={"ActionResult": "Success", "MessageID": "msg-001", "Status": "Pending", "Action": "Resubmit"},
        status=200,
    )

    resubmit = Resubmit(api_user)
    result = resubmit.SendRequest(channel="email", message_id="msg-001", send_time="2026-08-01T09:00:00")

    assert result.Result == "Success"
    assert json.loads(responses_lib.calls[0].request.body) == {"SendTime": "2026-08-01T09:00:00"}


@responses_lib.activate
def test_send_request_dispatches_to_fax_resubmit(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/fax/msg-002/resubmit",
        json={"ActionResult": "Success", "MessageID": "msg-002", "Status": "Pending", "Action": "Resubmit"},
        status=200,
    )

    resubmit = Resubmit(api_user)
    result = resubmit.SendRequest(channel="fax", message_id="msg-002", send_time="2026-08-01T09:00:00")

    assert result.Result == "Success"


@responses_lib.activate
def test_send_request_dispatches_to_tts_resubmit(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/tts/msg-003/resubmit",
        json={"ActionResult": "Success", "MessageID": "msg-003", "Status": "Pending", "Action": "Resubmit"},
        status=200,
    )

    resubmit = Resubmit(api_user)
    result = resubmit.SendRequest(channel="tts", message_id="msg-003", send_time="2026-08-01T09:00:00")

    assert result.Result == "Success"


@responses_lib.activate
def test_send_request_dispatches_to_voice_resubmit(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/voice/msg-004/resubmit",
        json={"ActionResult": "Success", "MessageID": "msg-004", "Status": "Pending", "Action": "Resubmit"},
        status=200,
    )

    resubmit = Resubmit(api_user)
    result = resubmit.SendRequest(channel="voice", message_id="msg-004", send_time="2026-08-01T09:00:00")

    assert result.Result == "Success"


@responses_lib.activate
def test_send_request_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/fax/ID123456/resubmit",
        json={"ActionResult": "Success", "MessageID": "ID123456", "Status": "Pending", "Action": "Resubmit"},
        status=200,
    )

    resubmit = Resubmit(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            resubmit.SendRequest(Channel="fax", MessageID="ID123456", SendTime="2026-08-01T09:00:00")
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_send_request_old_snake_case_kwargs_still_work_with_warning(api_user):
    mock_endpoint(
        responses_lib.PATCH,
        "/fax/ID123456/resubmit",
        json={"ActionResult": "Success", "MessageID": "ID123456", "Status": "Pending", "Action": "Resubmit"},
        status=200,
    )

    resubmit = Resubmit(api_user)
    with pytest.warns(DeprecationWarning):
        resubmit.SendRequest(channel="fax", message_id="ID123456", send_time="2026-08-01T09:00:00")
