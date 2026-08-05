import warnings

import pytest
import responses as responses_lib

from tnzapi.api.v300.reports.builders.status import Status
from tests.conftest import mock_endpoint


def test_poll_rejects_unknown_channel(api_user):
    status = Status(api_user)
    result = status.Poll(channel="workflow", message_id="msg-001")

    assert result.Result == "Failed"
    assert "workflow" in result.ErrorMessage[0].lower()


def test_poll_rejects_completely_invalid_channel(api_user):
    status = Status(api_user)
    result = status.Poll(channel="carrierpigeon", message_id="msg-001")

    assert result.Result == "Failed"
    assert "carrierpigeon" in result.ErrorMessage[0].lower()


@responses_lib.activate
def test_poll_dispatches_to_sms_status(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/sms/msg-001",
        json={"MessageID": "msg-001", "JobStatus": "Completed", "Recipients": []},
        status=200,
    )

    status = Status(api_user)
    result = status.Poll(channel="sms", message_id="msg-001")

    assert result.Result == "Success"
    assert result.MessageID == "msg-001"
    assert result.JobStatus == "Completed"


@responses_lib.activate
def test_poll_dispatches_to_email_status(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/email/msg-002",
        json={"MessageID": "msg-002", "JobStatus": "Pending", "Recipients": []},
        status=200,
    )

    status = Status(api_user)
    result = status.Poll(channel="email", message_id="msg-002")

    assert result.Result == "Success"
    assert result.MessageID == "msg-002"


@responses_lib.activate
def test_poll_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/sms/ID123456",
        json={"Result": "Success", "MessageID": "ID123456"},
        status=200,
    )

    status = Status(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            status.Poll(Channel="sms", MessageID="ID123456")
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

    status = Status(api_user)
    with pytest.warns(DeprecationWarning):
        status.Poll(channel="sms", message_id="ID123456")


def test_old_report_error_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="ReportErrorDTO is deprecated"):
        from tnzapi.api.v300.reports.models.responses.report_error import ReportErrorDTO

    from tnzapi.api.v300.reports.models.responses.report_error import ReportError
    assert ReportErrorDTO is ReportError
