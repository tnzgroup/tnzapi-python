import pytest

pytestmark = pytest.mark.integration


def test_status_poll(live_client, test_message_id, test_message_channel):
    result = live_client.Reports.Status.Poll(Channel=test_message_channel, MessageID=test_message_id)

    assert result.Result == "Success", result.ErrorMessage
