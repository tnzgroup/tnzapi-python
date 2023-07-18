import datetime

from dataclasses import dataclass

from tnzapi.helpers.functions import Functions


@dataclass
class SMSMessageInDTO:
    ID: str = None
    MessageID: str = None
    JobNum: str = None
    Account: str = None
    SubAccount: str = None
    Department: str = None
    Date: datetime.datetime = None
    DateUTC: datetime.datetime = None
    From: str = None
    MessageText: str = None
    Timezone: str = None

    def __repr__(self):
        return Functions.__pretty_class__(self, self)

