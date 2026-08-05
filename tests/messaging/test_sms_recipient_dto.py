import pytest

from tnzapi.core.model_conversion import convert_list_field
from tnzapi.api.v300.messaging.models.responses.sms_recipient import SMSRecipient
from tnzapi.api.v300.messaging.models.responses.sms_reply import SMSReply


def test_sms_recipient_dto_accepts_known_fields():
    recipient = SMSRecipient(
        Type="SMS",
        DestSeq="00000001",
        Destination="+64211234567",
        Status="Success",
        Result="Delivered",
        MessageText="Hello",
    )

    assert recipient.Destination == "+64211234567"
    assert recipient.Result == "Delivered"


def test_sms_recipient_dto_defaults_smsreplies_to_empty_list():
    recipient = SMSRecipient()

    assert recipient.SMSReplies == []


def test_sms_recipient_dto_converts_raw_reply_dicts_to_typed_instances():
    recipient = SMSRecipient(
        Destination="+64211234567",
        SMSReplies=[{"MessageText": "STOP", "From": "+64211234567"}],
    )

    assert len(recipient.SMSReplies) == 1
    assert isinstance(recipient.SMSReplies[0], SMSReply)
    assert recipient.SMSReplies[0].MessageText == "STOP"


def test_sms_recipient_dto_supports_dict_style_access():
    recipient = SMSRecipient(
        Destination="+64211234567",
        SMSReplies=[{"MessageText": "STOP"}],
    )

    assert recipient["Destination"] == "+64211234567"
    assert recipient.get("SMSReplies")[0]["MessageText"] == "STOP"


def test_sms_recipient_dto_smsreplies_none_does_not_crash():
    recipient = SMSRecipient(SMSReplies=None)

    assert recipient.SMSReplies is None


def test_sms_recipient_dto_reassigning_already_typed_replies_does_not_double_wrap():
    recipient = SMSRecipient()
    original_reply = SMSReply(MessageText="STOP")

    recipient.SMSReplies = [original_reply]

    assert recipient.SMSReplies[0] is original_reply


def test_sms_recipient_dto_preserves_unknown_fields_via_extras():
    recipient = convert_list_field(
        [{"Destination": "+64211234567", "SomeNewField": "value", "SMSReplies": []}],
        SMSRecipient,
    )[0]

    assert recipient["SomeNewField"] == "value"
    assert recipient.get("SomeNewField") == "value"
    assert "SomeNewField" in recipient


def test_old_sms_recipient_name_still_importable_and_warns():
    with pytest.warns(DeprecationWarning, match="SMSRecipientDTO is deprecated"):
        from tnzapi.api.v300.messaging.models.responses.sms_recipient import SMSRecipientDTO

    from tnzapi.api.v300.messaging.models.responses.sms_recipient import SMSRecipient
    assert SMSRecipientDTO is SMSRecipient
