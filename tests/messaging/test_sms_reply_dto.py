import pytest

from tnzapi.core.model_conversion import convert_list_field
from tnzapi.api.v300.messaging.models.responses.sms_reply import SMSReply


def test_sms_reply_dto_accepts_known_fields():
    reply = SMSReply(
        ReceivedID="rid-1",
        ReceivedTimeLocal="2026-07-29 10:00:00",
        ReceivedTimeUTC="2026-07-28 22:00:00",
        ReceivedTimeUTC_RFC3339="2026-07-28T22:00:00Z",
        Timezone="Pacific/Auckland",
        From="+64211234567",
        MessageText="STOP",
    )

    assert reply.ReceivedID == "rid-1"
    assert reply.MessageText == "STOP"


def test_sms_reply_dto_defaults_to_none():
    reply = SMSReply()

    assert reply.MessageText is None


def test_sms_reply_dto_supports_dict_style_access():
    reply = SMSReply(MessageText="STOP", From="+64211234567")

    assert reply["MessageText"] == "STOP"
    assert reply.get("From") == "+64211234567"
    assert "MessageText" in reply


def test_sms_reply_dto_preserves_unknown_fields_via_extras():
    reply = convert_list_field(
        [{"MessageText": "STOP", "SomeNewField": "value"}], SMSReply
    )[0]

    assert reply["SomeNewField"] == "value"
    assert reply.get("SomeNewField") == "value"
    assert "SomeNewField" in reply


def test_old_sms_reply_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="SMSReplyDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.sms_reply import SMSReplyDTO

    from tnzapi.api.v300.messaging.models.responses.sms_reply import SMSReply
    assert SMSReplyDTO is SMSReply
