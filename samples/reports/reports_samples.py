"""Reports sample code. Full field reference: README.md > Reports.

client.Reports exposes three properties, each returning a fresh request object
on every access: .Status (channel-agnostic dispatcher over Channel="sms"/
"email"/"fax"/"tts"/"voice"/"whatsapp"/"rcs" - not Workflow, which has no
Status(...) to dispatch to), .SMSReceived, and .SMSReply. The latter two are
thin SMS-only wrappers - SMSReceived.Poll(...) returns the same response as
client.Messaging.SMS.Received(...), and SMSReply.Poll(...) the same as
client.Messaging.SMS.Status(...)/Reply(...) - useful when you want the
Reports-facade naming/grouping rather than reaching into Messaging.SMS
directly. Prefer client.Reports when the channel isn't known until runtime
(e.g. a MessageID/Channel pair stored together in your own database); if you
already know the channel at the call site, calling it directly on
client.Messaging.<Channel> is simpler.
"""

from tnzapi import TNZAPI


class ReportsSamples:

    def __init__(self, client: TNZAPI = None):
        self.client = client or TNZAPI()

    def GetMessageStatus(self, Channel: str = "sms", MessageID: str = "ID123456"):
        client = self.client
        return client.Reports.Status.Poll(Channel=Channel, MessageID=MessageID)

    def GetSMSReceived(self):
        """Inbound SMS replies from the last 24 hours (TimePeriod is minutes, max 1440)."""
        client = self.client
        return client.Reports.SMSReceived.Poll(TimePeriod=1440)

    def GetSMSReceivedByDateRange(self):
        client = self.client
        return client.Reports.SMSReceived.Poll(
            DateFrom="2026-07-01 00:00:00",
            DateTo="2026-08-01 00:00:00",
        )

    def GetSMSReply(self, MessageID: str = "ID123456"):
        """SMSReply.Poll(...) is a thin alias over SMS's own Status(...) - there's no
        distinct reply-shaped response in v300. Replies show up on
        Recipients[].SMSReplies, same as calling
        client.Messaging.SMS.Status(...)/Reply(...) directly.
        """
        client = self.client
        return client.Reports.SMSReply.Poll(MessageID=MessageID)
