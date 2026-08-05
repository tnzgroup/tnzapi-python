import warnings
from urllib.parse import parse_qs, urlparse

import pytest
import responses as responses_lib

from tnzapi.api.v300.reports.builders.sms_received import SMSReceived
from tests.conftest import mock_endpoint


@responses_lib.activate
def test_poll_dispatches_to_sms_received(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/sms/received",
        json={
            "TotalRecords": 1, "RecordsPerPage": 20, "PageCount": 1, "Page": 1,
            "Messages": [{"ReceivedID": "a1b2c3d4-e5f6-7890-1234-567890abcdee", "From": "+6421000001", "MessageText": "Hi there"}],
        },
        status=200,
    )

    sms_received = SMSReceived(api_user)
    result = sms_received.Poll(time_period=10)

    assert result.Result == "Success"
    assert result.Messages[0]["MessageText"] == "Hi there"
    assert parse_qs(urlparse(responses_lib.calls[0].request.url).query)["timePeriod"] == ["10"]


@responses_lib.activate
def test_poll_new_pascalcase_kwargs_accepted(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/sms/received",
        json={"Result": "Success", "TotalRecords": 0, "Messages": []},
        status=200,
    )

    sms_received = SMSReceived(api_user)
    with warnings.catch_warnings():
        warnings.simplefilter("error", DeprecationWarning)
        try:
            sms_received.Poll(TimePeriod=10, RecordsPerPage=5, Page=2)
        except TypeError as exc:
            pytest.fail(f"PascalCase kwargs not accepted: {exc}")


@responses_lib.activate
def test_poll_old_snake_case_kwargs_still_work_with_warning(api_user):
    mock_endpoint(
        responses_lib.GET,
        "/sms/received",
        json={"Result": "Success", "TotalRecords": 0, "Messages": []},
        status=200,
    )

    sms_received = SMSReceived(api_user)
    with pytest.warns(DeprecationWarning):
        sms_received.Poll(time_period=10)
