"""WhatsApp sample code. Full field reference: README.md > Messaging > WhatsApp.

WhatsApp requires an approved TemplateID and a FromNumber (your registered
WhatsApp sender number) on every send.
"""

from tnzapi import TNZAPI
from tnzapi.core.destination import Destination
from tnzapi.core.file_attachment import FileAttachment
from tnzapi.core.send_mode import SendMode

from samples.messaging._pagination import WalkAllPages


class WhatsAppSamples:

    def __init__(self, client: TNZAPI = None):
        self.client = client or TNZAPI()

    def Send(self):
        client = self.client
        return client.Messaging.WhatsApp.SendMessage(
            TemplateID="[Your Template ID]",
            Message="Hi there!",
            FromNumber="+6495006000",
            Destination="+64211234567"
        )

    def SendInTestMode(self):
        """Mode=SendMode.Test validates the send without actually delivering
        it - equivalent to Mode="Test"."""
        client = self.client
        return (
            client.Messaging.WhatsApp
            .Set(
                TemplateID="[Your Template ID]",
                Message="Hi there!",
                FromNumber="+6495006000",
                Mode=SendMode.Test  # Test mode
            )
            .AddDestination("+64211234567")
            .SendMessage()
        )

    def SendUsingBuilder(self):
        client = self.client
        return (
            client.Messaging.WhatsApp
            .Set(
                TemplateID="[Your Template ID]",
                Message="Hi there!",
                FromNumber="+6495006000"
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
            client.Messaging.WhatsApp
            .Set(
                TemplateID="[Your Template ID]",
                Message="Hi [[FirstName]]!",
                FromNumber="+6495006000"
            )
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
            client.Messaging.WhatsApp
            .Set(
                TemplateID="[Your Template ID]",
                Message="See the attached documents.",
                FromNumber="+6495006000"
            )
            .AddDestination("+64211234567")
            .AddAttachments(["path/to/doc.pdf", "path/to/receipt.pdf"])
            .SendMessage()
        )

    def SendUsingAddressbookDestination(self):
        client = self.client
        return (
            client.Messaging.WhatsApp
            .Set(
                TemplateID="[Your Template ID]",
                Message="Hi [[FirstName]]!",
                FromNumber="+6495006000"
            )
            .AddDestination(ContactID="[Contact ID]")
            .AddDestination(GroupID="[Group ID]")
            .SendMessage()
        )

    def SendToMultipleRecipients(self):
        client = self.client
        return client.Messaging.WhatsApp.SendMessage(
            TemplateID="[Your Template ID]",
            Message="Hi there!",
            FromNumber="+6495006000",
            Destinations=[
                {"ToNumber": "+64211234567"},
                {"ToNumber": "+64211234568"}
            ]
        )

    def SendToMultipleRecipientsUsingTypedDestination(self):
        client = self.client
        return (
            client.Messaging.WhatsApp
            .Set(
                TemplateID="[Your Template ID]",
                Message="Hi [[FirstName]]!",
                FromNumber="+6495006000",
            )
            .AddDestinations([
                Destination(ToNumber="+64211234567", FirstName="Alice"),
                Destination(ToNumber="+64211234568", FirstName="Bob"),
            ])
            .SendMessage()
        )

    def SendWithFallback(self):
        client = self.client
        return client.Messaging.WhatsApp.SendMessage(
            TemplateID="[Your Template ID]",
            Message="Hi there!",
            FromNumber="+6495006000",
            Destination="+64211234567",
            FallbackMode="SMS",
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
        return client.Messaging.WhatsApp.SendMessage(
            TemplateID="[Your Template ID]",
            Message="Hi [[FirstName]]!",
            FromNumber="+6495006000",
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
            client.Messaging.WhatsApp
            .Set(
                TemplateID="[Your Template ID]",
                Message="Hi [[FirstName]]!",
                FromNumber="+6495006000"
            )
            .AddDestination(ContactID="[Contact ID 1]")
            .AddDestination(ContactID="[Contact ID 2]")
            .AddDestination(GroupID="[Group ID 1]")
            .AddDestination(GroupID="[Group ID 2]")
            .SendMessage()
        )

    def SendWithAttachment(self):
        """A file path is read and base64-encoded automatically."""
        client = self.client
        return (
            client.Messaging.WhatsApp
            .Set(
                TemplateID="[Your Template ID]",
                Message="See the attached document.",
                FromNumber="+6495006000"
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
            client.Messaging.WhatsApp
            .Set(
                TemplateID = "[Your Template ID]",
                Message = "See the attached document.",
                FromNumber = "+6495006000",
            )
            .AddDestination("+64211234567")
            .AddAttachment(
                FileAttachment("path/to/doc.pdf")
            )
            .SendMessage()
        )

    def Status(self, MessageID: str):
        client = self.client
        return client.Messaging.WhatsApp.Status(MessageID, RecordsPerPage=20, Page=1)

    def Received(self):
        client = self.client
        return client.Messaging.WhatsApp.Received(TimePeriod=1440, RecordsPerPage=20, Page=1)

    def ReceivedByDateRange(self):
        client = self.client
        return client.Messaging.WhatsApp.Received(
            DateFrom="2026-07-01 00:00:00",
            DateTo="2026-08-01 00:00:00",
            RecordsPerPage=20,
            Page=1
        )

    def GetAllInboundWhatsApp(self, TimePeriodMinutes: int = 1440):
        """Walk every page - Received() only ever returns the requested page,
        it never auto-walks on your behalf."""
        client = self.client
        result = WalkAllPages(client.Messaging.WhatsApp.Received, TimePeriodMinutes)
        if result.error:
            print("Walk stopped early:", result.error)
        print(f"Total inbound WhatsApp messages in the last {TimePeriodMinutes} minutes: {len(result.messages)}")
        return result.messages

    def Reschedule(self, MessageID: str):
        client = self.client
        return client.Messaging.WhatsApp.Reschedule(MessageID, SendTime="2026-08-01T09:00:00")

    def Abort(self, MessageID: str):
        client = self.client
        return client.Messaging.WhatsApp.Abort(MessageID)
