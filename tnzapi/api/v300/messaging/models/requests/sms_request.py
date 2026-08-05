from dataclasses import dataclass, field


@dataclass
class SMSRequest:
    Message: str = None
    TemplateID: str = None
    Destination: str = None
    ToNumber: str = None
    Destinations: list = field(default_factory=list)
    ContactID: str = None
    GroupID: str = None
    MessageID: str = None
    Reference: str = None
    NotificationType: str = None
    WebhookCallbackURL: str = None
    WebhookCallbackFormat: str = None
    ReportTo: str = None
    SendTime: str = None
    Timezone: str = None
    SubAccount: str = None
    Department: str = None
    FromNumber: str = None
    SMSEmailReply: str = None
    CharacterConversion: bool = False
    FallbackMode: str = None
    SMSCustomPageID: str = None
    Mode: str = None
    Files: list = field(default_factory=list)


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"SMSRequestDTO": SMSRequest})

__all__ = ["SMSRequest", "SMSRequestDTO"]
