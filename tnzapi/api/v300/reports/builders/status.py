from tnzapi.core.auth import TNZApiUser
from tnzapi.core.legacy_kwargs import accept_legacy_kwargs
from tnzapi.api.v300.reports.models.responses.report_error import ReportError


class Status:

    def __init__(self, user: TNZApiUser):
        self.user = user

    @accept_legacy_kwargs({
        "channel": "Channel", "message_id": "MessageID",
        "records_per_page": "RecordsPerPage", "page": "Page",
    })
    def Poll(self, Channel: str, MessageID: str, RecordsPerPage: int = 20, Page: int = 1):

        from tnzapi.api.v300.messaging.builders.sms import SMS
        from tnzapi.api.v300.messaging.builders.email import Email
        from tnzapi.api.v300.messaging.builders.fax import Fax
        from tnzapi.api.v300.messaging.builders.tts import TTS
        from tnzapi.api.v300.messaging.builders.voice import Voice
        from tnzapi.api.v300.messaging.builders.whatsapp import WhatsApp
        from tnzapi.api.v300.messaging.builders.rcs import RCS

        channel_classes = {
            "sms": SMS, "email": Email, "fax": Fax, "tts": TTS,
            "voice": Voice, "whatsapp": WhatsApp, "rcs": RCS,
        }

        channel_key = (Channel or "").lower()
        channel_class = channel_classes.get(channel_key)

        if channel_class is None:
            return ReportError(Result="Failed", ErrorMessage=[f"Unknown or unsupported channel for Status: {Channel}"])

        return channel_class(self.user).Status(MessageID, RecordsPerPage, Page)
