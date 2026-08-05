from tnzapi.core.auth import TNZApiUser
from tnzapi.core.legacy_kwargs import accept_legacy_kwargs
from tnzapi.api.v300.actions.models.responses.action_error import ActionError
from tnzapi.api.v300.actions.builders.abort import _resolve_channel

PACING_CHANNELS = ("tts", "voice")


class Pacing:

    def __init__(self, user: TNZApiUser):
        self.user = user

    @accept_legacy_kwargs({"channel": "Channel", "message_id": "MessageID", "number_of_operators": "NumberOfOperators"})
    def SendRequest(self, Channel: str, MessageID: str, NumberOfOperators: int):

        channel_key = (Channel or "").lower()

        if channel_key not in PACING_CHANNELS:
            return ActionError(Result="Failed", ErrorMessage=[f"Pacing is not supported for channel: {Channel}"])

        channel_class = _resolve_channel(channel_key)
        return channel_class(self.user).Pacing(MessageID, NumberOfOperators)
