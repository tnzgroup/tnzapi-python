"""Voice (pre-recorded audio) sample code. Full field reference: README.md > Messaging > Voice."""

from tnzapi import TNZAPI
from tnzapi.core.destination import Destination
from tnzapi.core.file_attachment import FileAttachment
from tnzapi.core.send_mode import SendMode


class VoiceSamples:

    def __init__(self, client: TNZAPI = None):
        self.client = client or TNZAPI()

    def Send(self):
        client = self.client
        return client.Messaging.Voice.SendMessage(
            MessageToPeople="path/to/audio.wav",
            MessageToAnswerPhones="path/to/audio.wav",
            Destinations=[{"ToNumber": "+64211232345"}],
            Reference="Voice Test - 64211232345",
            Keypads=[{"Tone": 1, "RouteNumber": "+6491232345"}]
        )

    def SendInTestMode(self):
        """Mode=SendMode.Test validates the send without actually delivering
        it - equivalent to Mode="Test"."""
        client = self.client
        return (
            client.Messaging.Voice
            .Set(
                MessageToPeople="path/to/audio.wav",
                Mode=SendMode.Test  # Test mode
            )
            .AddDestination("+64211232345")
            .SendMessage()
        )

    def SendWithKeypadMenu(self):
        client = self.client
        return (
            client.Messaging.Voice
            .Set(
                MessageToPeople="path/to/audio.wav",
                Reference="Voice Test - 64211232345",
            )
            .AddDestination("+64211232345")
            .AddKeypad(Tone=1, RouteNumber="+6491232345")
            .SendMessage()
        )

    def SendUsingAddKeypads(self):
        """AddKeypads([...]) adds several keypad entries in one call - each
        item is a plain dict of the same fields AddKeypad(...) takes."""
        client = self.client
        return (
            client.Messaging.Voice
            .Set(
                MessageToPeople="path/to/press-1-for-sales-2-for-support.wav",
                Reference="Voice Test - 64211232345",
            )
            .AddDestination("+64211232345")
            .AddKeypads([
                {"Tone": 1, "RouteNumber": "+6491001001"},
                {"Tone": 2, "RouteNumber": "+6491001002"},
            ])
            .SendMessage()
        )

    def SendUsingAddDestinations(self):
        """AddDestinations([...]) adds several destinations in one call - each
        item can be a bare string, a dict, or a typed Destination, mixed
        freely. AddDestination(...) (singular) only ever adds one and raises
        TypeError if given a list directly."""
        client = self.client
        return (
            client.Messaging.Voice
            .Set(MessageToPeople="path/to/audio.wav")
            .AddDestinations(["+64211232345", "+64211232346"])
            .SendMessage()
        )

    def SendFromFilePath(self):
        """Local audio file - read and base64-encoded automatically."""
        client = self.client
        return (
            client.Messaging.Voice
            .Set(
                MessageToPeople = "path/to/audio.wav",
            )
            .AddDestination("+64211232345")
            .SendMessage()
        )

    def SendUsingTypedFileAttachment(self):
        """MessageToPeople=FileAttachment("path/to/audio.wav") is equivalent to
        MessageToPeople="path/to/audio.wav" above - .Data is used, .Name is
        ignored, since this field has no filename concept."""
        client = self.client
        return (
            client.Messaging.Voice
            .Set(
                MessageToPeople = FileAttachment("path/to/audio.wav"),
            )
            .AddDestination("+64211232345")
            .SendMessage()
        )

    def SendToMultipleDestinations(self):
        client = self.client
        return (
            client.Messaging.Voice
            .Set(
                MessageToPeople="path/to/audio.wav"
            )
            .AddDestination("+64211232345")
            .AddDestination("+64211232346")
            .SendMessage()
        )

    def SendWithPersonalisation(self):
        """Personalisation fields can't be spoken by pre-recorded audio, but
        they're still accepted on the destination and echoed back in status
        reports."""
        client = self.client
        return (
            client.Messaging.Voice
            .Set(
                MessageToPeople="path/to/audio.wav"
            )
            .AddDestinations([
                Destination(
                    MainPhone="+64211232345",
                    FirstName="Alice",
                    Custom1="Account #4432",
                ),
                Destination(
                    MainPhone="+64211232346",
                    FirstName="Bob",
                    Custom1="Account #7788",
                ),
            ])
            .SendMessage()
        )

    def SendWithRetryCallerIdAndBillingCodes(self):
        client = self.client
        return client.Messaging.Voice.SendMessage(
            MessageToPeople="path/to/audio.wav",
            Destination="+64211232345",
            RetryAttempts=3,
            RetryPeriod=5,
            CallerID="+6491000000",
            SubAccount="Sales",
            Department="Outbound",
            ReportTo="reports@example.com",
        )

    def SendUsingAddressbookDestination(self):
        client = self.client
        return (
            client.Messaging.Voice
            .Set(
                MessageToPeople="path/to/audio.wav"
            )
            .AddDestination(ContactID="[Contact ID]")
            .AddDestination(GroupID="[Group ID]")
            .SendMessage()
        )

    def SendToMultipleContactsAndGroups(self):
        """Multiple ContactID/GroupID destinations in one call, flat style - every
        ID as its own Destinations entry.

        Unlike tnzapi-dotnet's named-parameter SendMessage(contactIDs=[...],
        groupIDs=[...]), there's no single list-kwarg for this here - see
        SendToMultipleContactsAndGroupsUsingBuilder() for the other
        equivalent way. Both produce the exact same Destinations array on
        the wire.
        """
        client = self.client
        return client.Messaging.Voice.SendMessage(
            MessageToPeople="path/to/audio.wav",
            Destinations=[
                {"ContactID": "[Contact ID 1]"},
                {"ContactID": "[Contact ID 2]"},
                {"GroupID": "[Group ID 1]"},
                {"GroupID": "[Group ID 2]"}
            ]
        )

    def SendToMultipleContactsAndGroupsUsingBuilder(self):
        """Same as SendToMultipleContactsAndGroups(), builder style - one
        AddDestination() call per ID."""
        client = self.client
        return (
            client.Messaging.Voice
            .Set(
                MessageToPeople="path/to/audio.wav"
            )
            .AddDestination(ContactID="[Contact ID 1]")
            .AddDestination(ContactID="[Contact ID 2]")
            .AddDestination(GroupID="[Group ID 1]")
            .AddDestination(GroupID="[Group ID 2]")
            .SendMessage()
        )

    def SendScheduled(self):
        client = self.client
        return client.Messaging.Voice.SendMessage(
            MessageToPeople="path/to/audio.wav",
            Destination="+64211232345",
            SendTime="2026-08-01T09:00:00",
            Timezone="Pacific/Auckland"
        )

    def SendIVRMenu(self):
        """Same keypad-routing fields as TTS, driven by recorded audio instead of
        text. Tone=3 just plays audio with no RouteNumber at all; Tone=9 uses
        PlaySection="Main" to let the caller replay the main message."""
        client = self.client
        return (
            client.Messaging.Voice
            .Set(
                MessageToPeople="path/to/press-1-for-sales-2-for-support.wav",
                Reference="IVR Test - 64211232345",
                KeypadOptionRequired=True,
                CallRouteMessageOnWrongKey="path/to/invalid-option.wav",
                CallRouteMessageToPeople="path/to/please-hold.wav",
                CallRouteMessageToOperators="path/to/incoming-ivr-call.wav",
                NumberOfOperators=2,
            )
            .AddDestination("+64211232345")
            .AddKeypad(Tone=1, RouteNumber="+6491001001")
            .AddKeypad(Tone=2, RouteNumber="+6491001002")
            .AddKeypad(Tone=3, Play="path/to/opening-hours.wav")
            .AddKeypad(Tone=9, PlaySection="Main")
            .SendMessage()
        )

    def Status(self, MessageID: str):
        client = self.client
        return client.Messaging.Voice.Status(MessageID, RecordsPerPage=20, Page=1)

    def Reschedule(self, MessageID: str):
        client = self.client
        return client.Messaging.Voice.Reschedule(MessageID, SendTime="2026-08-01T09:00:00")

    def Abort(self, MessageID: str):
        client = self.client
        return client.Messaging.Voice.Abort(MessageID)

    def Resubmit(self, MessageID: str):
        client = self.client
        return client.Messaging.Voice.Resubmit(MessageID, SendTime="2026-08-01T09:00:00")

    def Pacing(self, MessageID: str):
        client = self.client
        return client.Messaging.Voice.Pacing(MessageID, NumberOfOperators=10)
