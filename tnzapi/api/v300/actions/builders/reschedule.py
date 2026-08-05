from tnzapi.core.auth import TNZApiUser
from tnzapi.core.legacy_kwargs import accept_legacy_kwargs
from tnzapi.api.v300.actions.models.responses.action_error import ActionError
from tnzapi.api.v300.actions.builders.abort import _resolve_channel


class Reschedule:

    def __init__(self, user: TNZApiUser):
        self.user = user

    @accept_legacy_kwargs({"channel": "Channel", "message_id": "MessageID", "send_time": "SendTime"})
    def SendRequest(self, Channel: str, MessageID: str, SendTime: str):

        channel_class = _resolve_channel(Channel)

        if channel_class is None:
            return ActionError(Result="Failed", ErrorMessage=[f"Unknown or unsupported channel for Reschedule: {Channel}"])

        return channel_class(self.user).Reschedule(MessageID, SendTime)
