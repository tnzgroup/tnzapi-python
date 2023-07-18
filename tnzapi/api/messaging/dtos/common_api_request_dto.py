from dataclasses import dataclass, field
from datetime import datetime

from tnzapi.helpers.functions import Functions

@dataclass
class CommonApiRequestDTO:
    ErrorEmailNotify: str = None

    WebhookCallbackURL: str = None
    WebhookCallbackFormat: str = None

    MessageID: str = None

    Reference: str = None
    SendTime: datetime = None
    TimeZone: str = None
    SubAccount: str = None
    Department: str = None
    ChargeCode: str = None

    Destinations: list[str] = field(default_factory=list)

    def __repr__(self):
        return Functions.__pretty_class__(self, self)