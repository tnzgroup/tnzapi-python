from tnzapi.core.auth import TNZApiUser
from tnzapi.core.legacy_kwargs import accept_legacy_kwargs


class SMSReply:

    def __init__(self, user: TNZApiUser):
        self.user = user

    @accept_legacy_kwargs({
        "message_id": "MessageID", "records_per_page": "RecordsPerPage", "page": "Page",
    })
    def Poll(self, MessageID: str, RecordsPerPage: int = 20, Page: int = 1):

        from tnzapi.api.v300.messaging.builders.sms import SMS

        return SMS(self.user).Status(MessageID, RecordsPerPage, Page)
