import datetime

from dataclasses import dataclass, field

from tnzapi.api.reports.dtos.sms_reply_recipient_reply_dto import SMSReplyRecipientReplyDTO
from tnzapi.api.reports.dtos.recipient_dto import RecipientDTO

from tnzapi.helpers.functions import Functions


@dataclass
class SMSReplyRecipientDTO(RecipientDTO):
    MessageText: str = None
    SMSReplies: list[SMSReplyRecipientReplyDTO] = field(default_factory=list)

    def __repr__(self):
        return Functions.__pretty_class__(self, self)