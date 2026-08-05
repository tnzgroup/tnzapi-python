import warnings

import pytest
import responses as responses_lib

from tnzapi.api.v300.reports.builders.sms_reply import SMSReply
from tests.conftest import mock_endpoint


@responses_lib.activate
def test_poll_dispatches_to_sms_status(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/sms/msg-001",
        json={
            "MessageID": "msg-001",
            "JobStatus": "Completed",
            "Recipients": [{"Type": "SMS", "Destination": "+64211234567", "Status": "Success", "SMSReplies": [{"MessageText": "STOP"}]}],
        },
        status=200,
    )

    sms_reply = SMSReply(api_user)
    result = sms_reply.Poll(message_id="msg-001")

    assert result.Result == "Success"
    assert result.Recipients[0]["SMSReplies"][0]["MessageText"] == "STOP"


@responses_lib.activate
def test_poll_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/sms/ID123456",
        json={"Result": "Success", "MessageID": "ID123456"},
        status=200,
    )

    sms_reply = SMSReply(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            sms_reply.Poll(MessageID="ID123456")
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_poll_old_snake_case_kwargs_still_work_with_warning(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/sms/ID123456",
        json={"Result": "Success", "MessageID": "ID123456"},
        status=200,
    )

    sms_reply = SMSReply(api_user)
    with pytest.warns(DeprecationWarning):
        sms_reply.Poll(message_id="ID123456")
