import pytest

pytestmark = pytest.mark.integration


def test_optout_list(live_client):
    result = live_client.OptOut.List()

    assert result.Result == "Success", result.ErrorMessage
