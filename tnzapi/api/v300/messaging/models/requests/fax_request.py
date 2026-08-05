from dataclasses import dataclass, field


@dataclass
class FaxRequest:
    Files: list = field(default_factory=list)
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
    CSID: str = None
    Resolution: str = None
    WatermarkFolder: str = None
    WatermarkFirstPage: str = None
    WatermarkAllPages: str = None
    RetryAttempts: int = None
    RetryPeriod: int = None
    Mode: str = None


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"FaxRequestDTO": FaxRequest})

__all__ = ["FaxRequest", "FaxRequestDTO"]