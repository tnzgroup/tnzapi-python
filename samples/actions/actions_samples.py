"""Actions sample code. Full field reference: README.md > Actions.

Each action takes the messaging `Channel` ("sms", "email", "fax", "tts",
"voice", "whatsapp" or "rcs") plus the `MessageID` to act on. Resubmit only
applies to email/fax/tts/voice, and Pacing only to tts/voice. Equivalent
per-channel direct calls (e.g. client.Messaging.SMS.Reschedule(...)) also
exist - see samples/messaging/*_samples.py.
"""

from tnzapi import TNZAPI


class ActionsSamples:

    def __init__(self, client: TNZAPI = None):
        self.client = client or TNZAPI()

    def AbortAJob(self):
        client = self.client
        return client.Actions.Abort.SendRequest(
            Channel="sms",
            MessageID="ID123456"
        )

    def RescheduleAJob(self):
        client = self.client
        return client.Actions.Reschedule.SendRequest(
            Channel="sms",
            MessageID="ID123456",
            SendTime="2026-08-01T09:00:00"
        )

    def ResubmitAFailedJob(self):
        client = self.client
        return client.Actions.Resubmit.SendRequest(
            Channel="fax",
            MessageID="ID123456",
            SendTime="2026-08-01T09:00:00"
        )

    def AdjustPacing(self):
        client = self.client
        return client.Actions.Pacing.SendRequest(
            Channel="tts",
            MessageID="ID123456",
            NumberOfOperators=10
        )
