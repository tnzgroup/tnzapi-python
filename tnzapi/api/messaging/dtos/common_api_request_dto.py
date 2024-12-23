from dataclasses import dataclass, field
from datetime import datetime

from tnzapi.api.messaging.dtos.recipient_model import RecipientModel
from tnzapi.helpers.functions import Functions

@dataclass
class CommonApiRequestDTO:
    
    # Renaming ErrorEmailNotify -> ReportTo
    @property
    def ErrorEmailNotify(self):
        return self.ReportTo

    # Renaming ErrorEmailNotify -> ReportTo
    @ErrorEmailNotify.setter
    def ErrorEmailNotify(self, value):
        self.ReportTo = value

    ReportTo: str = None

    WebhookCallbackURL: str = None
    WebhookCallbackFormat: str = None

    MessageID: str = None

    Reference: str = None
    SendTime: datetime = None
    TimeZone: str = None
    SubAccount: str = None
    Department: str = None
    ChargeCode: str = None

    Destinations: list[RecipientModel] = field(default_factory=list)

    def __repr__(self):
        return Functions.__pretty_class__(self, self)