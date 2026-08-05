from dataclasses import dataclass


@dataclass
class _WebhookPayloadFields:
    """Shared field set for every TNZ webhook payload shape (see the OpenAPI
    spec's Webhooks section - ResultWebhookPayload and InboundSMSWebhookPayload
    use this same wire shape today)."""

    Version: str = None
    Sender: str = None
    APIKey: str = None
    Type: str = None
    Destination: str = None
    ContactID: str = None
    ReceivedID: str = None
    MessageID: str = None
    SubAccount: str = None
    Department: str = None
    JobNumber: str = None
    SentTimeLocal: str = None
    SendTimeUTC: str = None
    SentTimeUTC_RFC3339: str = None
    Status: str = None
    Result: str = None
    Message: str = None
    Price: str = None
    Detail: str = None
    URL: str = None


@dataclass
class ResultWebhookPayload(_WebhookPayloadFields):
    """A typed shape for the JSON body TNZ POSTs to a configured
    WebhookCallbackURL when a message's status changes. Construct one of
    these from the parsed request body in your own webhook receiver -
    this SDK never sends this payload, it only documents its shape."""


@dataclass
class InboundSMSWebhookPayload(_WebhookPayloadFields):
    """A typed shape for the JSON body TNZ POSTs to a configured
    WebhookCallbackURL when an inbound SMS reply arrives. Same field set
    as ResultWebhookPayload per the OpenAPI spec's Webhooks section -
    kept as a distinct class so a receiver's type hints communicate
    which kind of event it's handling, even though the wire shape
    happens to be identical today."""