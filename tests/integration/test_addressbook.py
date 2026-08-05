import pytest

pytestmark = pytest.mark.integration


def test_contact_list(live_client):
    result = live_client.Addressbook.Contact.List()

    assert result.Result == "Success", result.ErrorMessage
