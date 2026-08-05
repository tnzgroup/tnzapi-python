from dataclasses import fields

from tnzapi.webhooks import ResultWebhookPayload, InboundSMSWebhookPayload


def test_result_webhook_payload_has_expected_fields():
    field_names = {f.name for f in fields(ResultWebhookPayload)}

    assert field_names == {
        "Version", "Sender", "APIKey", "Type", "Destination", "ContactID",
        "ReceivedID", "MessageID", "SubAccount", "Department", "JobNumber",
        "SentTimeLocal", "SendTimeUTC", "SentTimeUTC_RFC3339", "Status",
        "Result", "Message", "Price", "Detail", "URL",
    }


def test_result_webhook_payload_constructs_from_a_json_like_dict():
    payload = ResultWebhookPayload(
        Version="1.0",
        MessageID="msg-001",
        Status="Delivered",
        Result="Success",
    )

    assert payload.MessageID == "msg-001"
    assert payload.Status == "Delivered"
    assert payload.Sender is None


def test_inbound_sms_webhook_payload_has_expected_fields():
    field_names = {f.name for f in fields(InboundSMSWebhookPayload)}

    assert field_names == {
        "Version", "Sender", "APIKey", "Type", "Destination", "ContactID",
        "ReceivedID", "MessageID", "SubAccount", "Department", "JobNumber",
        "SentTimeLocal", "SendTimeUTC", "SentTimeUTC_RFC3339", "Status",
        "Result", "Message", "Price", "Detail", "URL",
    }


def test_inbound_sms_webhook_payload_constructs_from_a_json_like_dict():
    payload = InboundSMSWebhookPayload(
        Version="1.0",
        ReceivedID="recv-001",
        Message="Hello back",
        Destination="+64211234567",
    )

    assert payload.ReceivedID == "recv-001"
    assert payload.Message == "Hello back"