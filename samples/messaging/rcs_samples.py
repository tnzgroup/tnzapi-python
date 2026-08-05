"""RCS sample code. Full field reference: README.md > Messaging > RCS.

Regional availability: RCS is not supported in New Zealand or Australia. Confirm
destination coverage before relying on RCS as a primary channel.
"""

from tnzapi import TNZAPI
from tnzapi.core.destination import Destination
from tnzapi.core.file_attachment import FileAttachment
from tnzapi.core.send_mode import SendMode

from samples.messaging._pagination import WalkAllPages


class RCSSamples:

    def __init__(self, client: TNZAPI = None):
        self.client = client or TNZAPI()

    def Send(self):
        client = self.client
        return client.Messaging.RCS.SendMessage(
            Message="Hi there!",
            Destination="+64211234567"
        )

    def SendInTestMode(self):
        """Mode=SendMode.Test validates the send without actually delivering
        it - equivalent to Mode="Test"."""
        client = self.client
        return (
            client.Messaging.RCS
            .Set(
                Message="Hi there!",
                Mode=SendMode.Test  # Test mode
            )
            .AddDestination("+64211234567")
            .SendMessage()
        )

    def SendUsingBuilder(self):
        client = self.client
        return (
            client.Messaging.RCS
            .Set(
                Message="Hi there!"
            )
            .AddDestination("+64211234567")
            .SendMessage()
        )

    def SendUsingAddDestinations(self):
        """AddDestinations([...]) adds several destinations in one call - each
        item can be a bare string, a dict, or a typed Destination, mixed
        freely. AddDestination(...) (singular) only ever adds one and raises
        TypeError if given a list directly."""
        client = self.client
        return (
            client.Messaging.RCS
            .Set(Message="Hi [[FirstName]]!")
            .AddDestinations([
                "+64211234567",
                {"ToNumber": "+64211234568", "FirstName": "Bob"},
            ])
            .SendMessage()
        )

    def SendUsingAddAttachments(self):
        """AddAttachments([...]) adds several attachments in one call - each
        item can be a path string, a dict, or a FileAttachment instance."""
        client = self.client
        return (
            client.Messaging.RCS
            .Set(Message="See the attached documents.")
            .AddDestination("+64211234567")
            .AddAttachments(["path/to/doc.pdf", "path/to/receipt.pdf"])
            .SendMessage()
        )

    def SendWithCustomSenderId(self):
        """FromNumber is E.164 without a leading '+', unlike every other phone
        field in this SDK."""
        client = self.client
        return (
            client.Messaging.RCS
            .Set(
                Message="Hi there!",
                FromNumber="61410023004",
            )
            .AddDestination("+64211234567")
            .SendMessage()
        )

    def SendWithFallback(self):
        client = self.client
        return client.Messaging.RCS.SendMessage(
            Message="Hi there!",
            Destination="+64211234567",
            FallbackMode="SMS",
        )

    def SendUsingAddressbookDestination(self):
        client = self.client
        return (
            client.Messaging.RCS
            .Set(
                Message="Hi [[FirstName]]!"
            )
            .AddDestination(ContactID="[Contact ID]")
            .AddDestination(GroupID="[Group ID]")
            .SendMessage()
        )

    def SendToMultipleRecipients(self):
        client = self.client
        return client.Messaging.RCS.SendMessage(
            Message="Hi there!",
            Destinations=[
                {"ToNumber": "+64211234567"},
                {"ToNumber": "+64211234568"},
            ],
        )

    def SendToMultipleRecipientsUsingTypedDestination(self):
        client = self.client
        return (
            client.Messaging.RCS
            .Set(Message="Hi [[FirstName]]!")
            .AddDestinations([
                Destination(ToNumber="+64211234567", FirstName="Alice"),
                Destination(ToNumber="+64211234568", FirstName="Bob"),
            ])
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
        return client.Messaging.RCS.SendMessage(
            Message="Hi [[FirstName]]!",
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
            client.Messaging.RCS
            .Set(
                Message="Hi [[FirstName]]!"
            )
            .AddDestination(ContactID="[Contact ID 1]")
            .AddDestination(ContactID="[Contact ID 2]")
            .AddDestination(GroupID="[Group ID 1]")
            .AddDestination(GroupID="[Group ID 2]")
            .SendMessage()
        )

    def SendScheduled(self):
        client = self.client
        return client.Messaging.RCS.SendMessage(
            Message="Hi there!",
            Destination="+64211234567",
            SendTime="2026-08-01T09:00:00",
            Timezone="Pacific/Auckland"
        )

    def SendWithAttachment(self):
        client = self.client
        return (
            client.Messaging.RCS
            .Set(
                Message="See the attached document."
            )
            .AddDestination("+64211234567")
            .AddAttachment("path/to/doc.pdf")
            .SendMessage()
        )

    def SendWithAttachmentFromFilePath(self):
        """A file path is read and base64-encoded automatically -
        FileAttachment("path/to/doc.pdf") is equivalent to
        FileAttachment(FileName="path/to/doc.pdf")."""
        client = self.client
        return (
            client.Messaging.RCS
            .Set(Message = "See the attached document.")
            .AddDestination("+64211234567")
            .AddAttachment(
                FileAttachment("path/to/doc.pdf")
            )
            .SendMessage()
        )

    def Status(self, MessageID: str):
        client = self.client
        return client.Messaging.RCS.Status(MessageID, RecordsPerPage=20, Page=1)

    def Received(self):
        client = self.client
        return client.Messaging.RCS.Received(TimePeriod=1440, RecordsPerPage=20, Page=1)

    def ReceivedByDateRange(self):
        client = self.client
        return client.Messaging.RCS.Received(
            DateFrom="2026-07-01 00:00:00",
            DateTo="2026-08-01 00:00:00",
            RecordsPerPage=20,
            Page=1
        )

    def GetAllInboundRCS(self, TimePeriodMinutes: int = 1440):
        """Walk every page - Received() only ever returns the requested page,
        it never auto-walks on your behalf."""
        client = self.client
        result = WalkAllPages(client.Messaging.RCS.Received, TimePeriodMinutes)
        if result.error:
            print("Walk stopped early:", result.error)
        print(f"Total inbound RCS messages in the last {TimePeriodMinutes} minutes: {len(result.messages)}")
        return result.messages

    def Reschedule(self, MessageID: str):
        client = self.client
        return client.Messaging.RCS.Reschedule(MessageID, SendTime="2026-08-01T09:00:00")

    def Abort(self, MessageID: str):
        client = self.client
        return client.Messaging.RCS.Abort(MessageID)
