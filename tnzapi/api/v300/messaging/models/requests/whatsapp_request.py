from dataclasses import dataclass, field


@dataclass
class WhatsAppRequest:
    TemplateID: str = None
    Message: str = None
    FallbackMode: str = None
    Files: list = field(default_factory=list)
    FromNumber: str = None
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
    Mode: str = None


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"WhatsAppRequestDTO": WhatsAppRequest})

__all__ = ["WhatsAppRequest", "WhatsAppRequestDTO"]
