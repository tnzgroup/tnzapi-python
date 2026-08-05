import pytest

pytestmark = pytest.mark.integration


def test_abort_send_request(live_client, test_message_id, test_message_channel):
    # Abort is only meaningfully "Success" while the target message is still
    # pending delivery - TNZ_TEST_MESSAGE_ID will very likely already be
    # delivered/expired by the time this runs. This asserts the round trip
    # completes and returns a real API response, not that the abort succeeds.
    result = live_client.Actions.Abort.SendRequest(Channel=test_message_channel, MessageID=test_message_id)

    assert result.Result in ("Success", "Failed"), result
    if result.Result == "Failed":
        assert result.ErrorMessage
