import datetime
import json
from dataclasses import dataclass, field

from tnzapi.api.reports.dtos.recipient_dto import RecipientDTO
from tnzapi.helpers.functions import Functions

@dataclass
class StatusDTO:
    Result: str = None
    MessageID: str = None
    Status: str = None
    JobNum: str = None
    Account: str = None
    SubAccount: str = None
    Department: str = None
    Reference: str = None
    CreatedTimeLocal: datetime.datetime = None
    CreatedTimeUTC: datetime.datetime = None
    CreatedTimeUTC_RFC3339: datetime.datetime = None
    DelayedTimeLocal: datetime.datetime = None
    DelayedTimeUTC: datetime.datetime = None
    DelayedTimeUTC_RFC3339: datetime.datetime = None
    Timezone: str = None
    Count: int = 0
    Complete: int = 0
    Success: int = 0
    Failed: int = 0
    Price: float = 0.00
    TotalRecords: int = 0
    RecordsPerPage: int = 0
    PageCount: int = 1
    Page: int = 1
    Recipients: list[RecipientDTO] = field(default_factory=list)
    ErrorMessage: list[str] = field(default_factory=list)

    def __repr__(self):
        return Functions.__pretty_class__(self, self)
    