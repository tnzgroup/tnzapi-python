"""TTS (Text-to-Speech) sample code. Full field reference: README.md > Messaging > TTS."""

from tnzapi import TNZAPI
from tnzapi.core.destination import Destination
from tnzapi.core.send_mode import SendMode


class TTSSamples:

    def __init__(self, client: TNZAPI = None):
        self.client = client or TNZAPI()

    def Send(self):
        client = self.client
        return client.Messaging.TTS.SendMessage(
            MessageToPeople="Hi there!",
            Destinations=[{"ToNumber": "+64211232345"}],
            Reference="Voice Test - 64211232345",
            Keypads=[{"Tone": 1, "Play": "You pressed 1", "RouteNumber": "+6491232345"}]
        )

    def SendInTestMode(self):
        """Mode=SendMode.Test validates the send without actually delivering
        it - equivalent to Mode="Test"."""
        client = self.client
        return (
            client.Messaging.TTS
            .Set(
                MessageToPeople="Hi there!",
                Mode=SendMode.Test  # Test mode
            )
            .AddDestination("+64211232345")
            .SendMessage()
        )

    def SendWithKeypadMenu(self):
        client = self.client
        return (
            client.Messaging.TTS
            .Set(
                MessageToPeople="Hi there!",
                Reference="Voice Test - 64211232345",
            )
            .AddDestination("+64211232345")
            .AddKeypad(
                Tone=1,
                Play="You pressed 1",
                RouteNumber="+6491232345",
            )
            .SendMessage()
        )

    def SendUsingAddKeypads(self):
        """AddKeypads([...]) adds several keypad entries in one call - each
        item is a plain dict of the same fields AddKeypad(...) takes."""
        client = self.client
        return (
            client.Messaging.TTS
            .Set(
                MessageToPeople="Press 1 for sales, press 2 for support.",
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
            client.Messaging.TTS
            .Set(MessageToPeople="Hi there!")
            .AddDestinations(["+64211232345", "+64211232346"])
            .SendMessage()
        )

    def SendToMultipleDestinations(self):
        client = self.client
        return (
            client.Messaging.TTS
            .Set(
                MessageToPeople="Hi there!"
            )
            .AddDestination("+64211232345")
            .AddDestination("+64211232346")
            .SendMessage()
        )

    def SendWithPersonalisation(self):
        client = self.client
        return (
            client.Messaging.TTS
            .Set(
                MessageToPeople="Hi [[FirstName]], your appointment is on [[Custom1]]."
            )
            .AddDestinations([
                Destination(
                    MainPhone="+64211232345",
                    FirstName="Alice",
                    Custom1="Monday 3pm",
                ),
                Destination(
                    MainPhone="+64211232346",
                    FirstName="Bob",
                    Custom1="Tuesday 10am",
                ),
            ])
            .SendMessage()
        )

    def SendWithRetryCallerIdAndReporting(self):
        client = self.client
        return client.Messaging.TTS.SendMessage(
            MessageToPeople="Hi there!",
            Destination="+64211232345",
            RetryAttempts=3,
            RetryPeriod=15,
            CallerID="+6491000000",
            Voice="Female",
            ReportTo="reports@example.com",
        )

    def SendUsingAddressbookDestination(self):
        client = self.client
        return (
            client.Messaging.TTS
            .Set(
                MessageToPeople="Hi there!"
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
        return client.Messaging.TTS.SendMessage(
            MessageToPeople="Hi there!",
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
            client.Messaging.TTS
            .Set(
                MessageToPeople="Hi there!"
            )
            .AddDestination(ContactID="[Contact ID 1]")
            .AddDestination(ContactID="[Contact ID 2]")
            .AddDestination(GroupID="[Group ID 1]")
            .AddDestination(GroupID="[Group ID 2]")
            .SendMessage()
        )

    def SendScheduled(self):
        client = self.client
        return client.Messaging.TTS.SendMessage(
            MessageToPeople="Hi there!",
            Destination="+64211232345",
            SendTime="2026-08-01T09:00:00",
            Timezone="Pacific/Auckland"
        )

    def SendIVRMenu(self):
        """Multi-option IVR routing, what to do on an unrecognised key press, a
        keypad that just plays a message with no RouteNumber at all (Tone=3),
        and a keypad that lets the caller replay the main message via
        PlaySection="Main" instead of Play/RouteNumber (Tone=9)."""
        client = self.client
        return (
            client.Messaging.TTS
            .Set(
                MessageToPeople="Press 1 for sales, press 2 for support.",
                Reference="IVR Test - 64211232345",
                KeypadOptionRequired=True,
                CallRouteMessageOnWrongKey="Sorry, that wasn't a valid option.",
                CallRouteMessageToPeople="Please hold while we transfer your call.",
                CallRouteMessageToOperators="Incoming call from the IVR menu.",
                NumberOfOperators=2,
            )
            .AddDestination("+64211232345")
            .AddKeypad(
                Tone=1,
                Play="Transferring you to sales.",
                RouteNumber="+6491001001",
            )
            .AddKeypad(
                Tone=2,
                Play="Transferring you to support.",
                RouteNumber="+6491001002",
            )
            .AddKeypad(
                Tone=3,
                Play="Here are our opening hours.",
            )
            .AddKeypad(
                Tone=9,
                PlaySection="Main",
            )
            .SendMessage()
        )

    def Status(self, MessageID: str):
        client = self.client
        return client.Messaging.TTS.Status(MessageID, RecordsPerPage=20, Page=1)

    def Reschedule(self, MessageID: str):
        client = self.client
        return client.Messaging.TTS.Reschedule(MessageID, SendTime="2026-08-01T09:00:00")

    def Abort(self, MessageID: str):
        client = self.client
        return client.Messaging.TTS.Abort(MessageID)

    def Resubmit(self, MessageID: str):
        client = self.client
        return client.Messaging.TTS.Resubmit(MessageID, SendTime="2026-08-01T09:00:00")

    def Pacing(self, MessageID: str):
        """Adjust the number of concurrent operators handling this job's callbacks."""
        client = self.client
        return client.Messaging.TTS.Pacing(MessageID, NumberOfOperators=10)
