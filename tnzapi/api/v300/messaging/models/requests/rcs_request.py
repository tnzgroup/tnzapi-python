from dataclasses import dataclass, field


@dataclass
class RCSRequest:
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
    SendTime: str = None
    Timezone: str = None
    SubAccount: str = None
    Department: str = None
    FromNumber: str = None
    SMSEmailReply: str = None
    CharacterConversion: bool = False
    Files: list = field(default_factory=list)
    FallbackMode: str = None
    Mode: str = None


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"RCSRequestDTO": RCSRequest})

__all__ = ["RCSRequest", "RCSRequestDTO"]
