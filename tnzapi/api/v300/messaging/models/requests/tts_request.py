from dataclasses import dataclass, field


@dataclass
class TTSRequest:
    MessageToPeople: str = None
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
    MessageToAnswerPhones: str = None
    AnswerPhoneMode: str = None
    Keypads: list = field(default_factory=list)
    KeypadOptionRequired: bool = False
    CallRouteMessageOnWrongKey: str = None
    CallRouteMessageToPeople: str = None
    CallRouteMessageToOperators: str = None
    NumberOfOperators: int = None
    RetryAttempts: int = None
    RetryPeriod: int = None
    CallerID: str = None
    Voice: str = None
    Options: str = None
    Mode: str = None


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"TTSRequestDTO": TTSRequest})

__all__ = ["TTSRequest", "TTSRequestDTO"]