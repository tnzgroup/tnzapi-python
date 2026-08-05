from tnzapi.core.auth import TNZApiUser
from tnzapi.core.legacy_kwargs import accept_legacy_kwargs
from tnzapi.api.v300.actions.models.responses.action_error import ActionError


def _resolve_channel(channel: str):

    from tnzapi.api.v300.messaging.builders.sms import SMS
    from tnzapi.api.v300.messaging.builders.email import Email
    from tnzapi.api.v300.messaging.builders.fax import Fax
    from tnzapi.api.v300.messaging.builders.tts import TTS
    from tnzapi.api.v300.messaging.builders.voice import Voice
    from tnzapi.api.v300.messaging.builders.whatsapp import WhatsApp
    from tnzapi.api.v300.messaging.builders.rcs import RCS

    return {
        "sms": SMS, "email": Email, "fax": Fax, "tts": TTS,
        "voice": Voice, "whatsapp": WhatsApp, "rcs": RCS,
    }.get((channel or "").lower())


class Abort:

    def __init__(self, user: TNZApiUser):
        self.user = user

    @accept_legacy_kwargs({"channel": "Channel", "message_id": "MessageID"})
    def SendRequest(self, Channel: str, MessageID: str):

        channel_class = _resolve_channel(Channel)

        if channel_class is None:
            return ActionError(Result="Failed", ErrorMessage=[f"Unknown or unsupported channel for Abort: {Channel}"])

        return channel_class(self.user).Abort(MessageID)
