from tnzapi.core.auth import TNZApiUser
from tnzapi.core.legacy_kwargs import accept_legacy_kwargs
from tnzapi.api.v300.actions.models.responses.action_error import ActionError
from tnzapi.api.v300.actions.builders.abort import _resolve_channel

RESUBMIT_CHANNELS = ("email", "fax", "tts", "voice")


class Resubmit:

    def __init__(self, user: TNZApiUser):
        self.user = user

    @accept_legacy_kwargs({"channel": "Channel", "message_id": "MessageID", "send_time": "SendTime"})
    def SendRequest(self, Channel: str, MessageID: str, SendTime: str):

        channel_key = (Channel or "").lower()

        if channel_key not in RESUBMIT_CHANNELS:
            return ActionError(Result="Failed", ErrorMessage=[f"Resubmit is not supported for channel: {Channel}"])

        channel_class = _resolve_channel(channel_key)
        return channel_class(self.user).Resubmit(MessageID, SendTime)
