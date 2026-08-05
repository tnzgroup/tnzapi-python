# v204's SMSApi reads/writes process-global state via tnzapi._config (mutated by
# other tests, e.g. tests/test_tnzapi.py's TNZAPI(AuthToken=...) construction) -
# every test in this file must be auth-independent to avoid order-dependent
# flakiness. None of the tests below need an AuthToken/Sender/APIKey.
from tnzapi.api.v204.messaging.requests.sms_api import SMSApi
from tnzapi.helpers.functions import Functions


def test_message_text_kwarg_maps_to_message_field():
    sms = SMSApi({"MessageText": "hi"})

    assert sms.APIMessageData.Message == "hi"


def test_message_text_property_reads_message_field():
    sms = SMSApi({"MessageText": "hi"})

    assert sms.MessageText == "hi"


def test_message_text_setter_writes_message_field():
    sms = SMSApi({"MessageText": "hi"})

    sms.MessageText = "changed"

    assert sms.APIMessageData.Message == "changed"


def test_message_text_setter_does_not_leak_a_stray_field_into_the_payload():
    sms = SMSApi({"MessageText": "hi", "Recipients": ["+64211234567"]})

    sms.MessageText = "changed"

    body = Functions.__json_dump_dto__(sms, sms.APIMessageData)

    assert '"Message": "changed"' in body
    assert "MessageText" not in body


def test_representative_kwargs_map_to_dto_fields():
    sms = SMSApi({"MessageText": "hi", "Reference": "ref-1", "FromNumber": "+64211111111"})

    assert sms.APIMessageData.Reference == "ref-1"
    assert sms.APIMessageData.FromNumber == "+64211111111"


def test_recipients_kwarg_builds_destination_dicts_via_add_recipient():
    sms = SMSApi({"MessageText": "hi", "Recipients": ["+64211234567"]})

    assert sms.Recipients == [{"Recipient": "+64211234567"}]


def test_recipients_are_only_merged_into_destinations_at_send_time_not_construction():
    sms = SMSApi({"MessageText": "hi", "Recipients": ["+64211234567"]})

    assert sms.APIMessageData.Destinations == []
