from dataclasses import dataclass, field


@dataclass
class EmailRequest:
    MessagePlain: str = None
    MessageHTML: str = None
    TemplateID: str = None
    Destination: str = None
    EmailAddress: str = None
    ContactID: str = None
    GroupID: str = None
    Destinations: list = field(default_factory=list)
    MessageID: str = None
    Reference: str = None
    From: str = None
    FromEmail: str = None
    CCEmail: str = None
    BCCEmail: str = None
    ReplyTo: str = None
    EmailSubject: str = None
    NotificationType: str = None
    WebhookCallbackURL: str = None
    WebhookCallbackFormat: str = None
    ReportTo: str = None
    SendTime: str = None
    Timezone: str = None
    SubAccount: str = None
    Department: str = None
    Files: list = field(default_factory=list)
    Mode: str = None


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"EmailRequestDTO": EmailRequest})

__all__ = ["EmailRequest", "EmailRequestDTO"]