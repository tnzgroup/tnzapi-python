import datetime

from dataclasses import dataclass, field

from tnzapi.helpers.functions import Functions


@dataclass
class RecipientDTO:
    Type: str = None
    DestSeq: str = None
    Destination: str = None
    Status: str = None
    Result: str = None
    SentDate: datetime.datetime = None
    SentDateUTC: datetime.datetime = None
    Attention: str = None
    Company: str = None
    Custom1: str = None
    Custom2: str = None
    Custom3: str = None
    Custom4: str = None
    Custom5: str = None
    Custom6: str = None
    Custom7: str = None
    Custom8: str = None
    Custom9: str = None
    RemoteID: str = None
    Price: float = 0.00

    def __repr__(self):
        return Functions.__pretty_class__(self, self)