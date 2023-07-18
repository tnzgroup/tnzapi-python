from dataclasses import dataclass, field
from datetime import datetime

from tnzapi.api.messaging.dtos.common_api_request_dto import CommonApiRequestDTO
from tnzapi.helpers.functions import Functions

@dataclass
class EmailApiRequestDTO(CommonApiRequestDTO):
    EmailSubject: str = None
    SMTPFrom: str = None
    From: str = None
    FromEmail: str = None
    CCEmail: str = None
    ReplyTo: str = None
    MessagePlain: str = None
    MessageHTML: str = None
    Files: list[str] = field(default_factory=list)
    Mode: str = None

    def __repr__(self):
        return Functions.__pretty_class__(self, self)
