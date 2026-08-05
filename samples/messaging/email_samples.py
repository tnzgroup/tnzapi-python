"""Email sample code. Full field reference: README.md > Messaging > Email."""

from tnzapi import TNZAPI
from tnzapi.core.destination import Destination
from tnzapi.core.file_attachment import FileAttachment
from tnzapi.core.send_mode import SendMode


class EmailSamples:

    def __init__(self, client: TNZAPI = None):
        self.client = client or TNZAPI()

    def Send(self):
        client = self.client
        return client.Messaging.Email.SendMessage(
            EmailSubject="Test Email",
            MessagePlain="Hi world!",
            Destination="recipient@example.com"
        )

    def SendInTestMode(self):
        """Mode=SendMode.Test validates the send without actually delivering
        it - equivalent to Mode="Test"."""
        client = self.client
        return (
            client.Messaging.Email
            .Set(
                EmailSubject="Test Email",
                MessagePlain="Hi world!",
                Mode=SendMode.Test  # Test mode
            )
            .AddDestination("recipient@example.com")
            .SendMessage()
        )

    def SendUsingBuilder(self):
        client = self.client
        return (
            client.Messaging.Email
            .Set(
                EmailSubject="Test Email",
                MessagePlain="Hi world!"
            )
            .AddDestination("recipient@example.com")
            .SendMessage()
        )

    def SendUsingAddDestinations(self):
        """AddDestinations([...]) adds several destinations in one call - each
        item can be a bare string, a dict, or a typed Destination, mixed
        freely. AddDestination(...) (singular) only ever adds one and raises
        TypeError if given a list directly."""
        client = self.client
        return (
            client.Messaging.Email
            .Set(EmailSubject="Test Email", MessagePlain="Hi [[FirstName]]!")
            .AddDestinations([
                "recipient@example.com",
                {"EmailAddress": "bob@example.com", "FirstName": "Bob"},
            ])
            .SendMessage()
        )

    def SendUsingAddAttachments(self):
        """AddAttachments([...]) adds several attachments in one call - each
        item can be a path string, a dict, or a FileAttachment instance."""
        client = self.client
        return (
            client.Messaging.Email
            .Set(
                EmailSubject="Test Email with Attachments",
                MessagePlain="See the attached documents."
            )
            .AddDestination("recipient@example.com")
            .AddAttachments(["path/to/doc.pdf", "path/to/invoice.pdf"])
            .SendMessage()
        )

    def SendUsingAddressbookDestination(self):
        client = self.client
        return (
            client.Messaging.Email
            .Set(EmailSubject="Test Email", MessagePlain="Hi [[FirstName]]!")
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
        return client.Messaging.Email.SendMessage(
            EmailSubject="Test Email",
            MessagePlain="Hi [[FirstName]]!",
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
            client.Messaging.Email
            .Set(EmailSubject="Test Email", MessagePlain="Hi [[FirstName]]!")
            .AddDestination(ContactID="[Contact ID 1]")
            .AddDestination(ContactID="[Contact ID 2]")
            .AddDestination(GroupID="[Group ID 1]")
            .AddDestination(GroupID="[Group ID 2]")
            .SendMessage()
        )

    def SendWithPersonalisationUsingTypedDestination(self):
        """Per-destination personalisation via typed Destination instances,
        builder style."""
        client = self.client
        return (
            client.Messaging.Email
            .Set(
                EmailSubject="Test Email",
                MessagePlain="Hi [[FirstName]], your appointment is on [[Custom1]]."
            )
            .AddDestinations([
                Destination(
                    EmailAddress="alice@example.com",
                    FirstName="Alice",
                    Custom1="Monday 3pm",
                ),
                Destination(
                    EmailAddress="bob@example.com",
                    FirstName="Bob",
                    Custom1="Tuesday 10am",
                ),
            ])
            .SendMessage()
        )

    def SendHtmlEmail(self):
        client = self.client
        return client.Messaging.Email.SendMessage(
            EmailSubject="Test Email",
            MessageHTML="<h1>Hi world!</h1><p>This is an HTML email.</p>",
            Destination="recipient@example.com"
        )

    def SendWithAttachment(self):
        """A file path is read and base64-encoded automatically."""
        client = self.client
        return (
            client.Messaging.Email
            .Set(
                EmailSubject="Test Email with Attachment",
                MessagePlain="See the attached document."
            )
            .AddDestination("recipient@example.com")
            .AddAttachment("path/to/doc.pdf")
            .SendMessage()
        )

    def SendWithAttachmentFromFilePath(self):
        """A file path is read and base64-encoded automatically -
        FileAttachment("path/to/doc.pdf") is equivalent to
        FileAttachment(FileName="path/to/doc.pdf")."""
        client = self.client
        return (
            client.Messaging.Email
            .Set(
                EmailSubject = "Test Email with Attachment",
                MessagePlain = "See the attached document.",
            )
            .AddDestination("recipient@example.com")
            .AddAttachment(
                FileAttachment("path/to/doc.pdf")
            )
            .SendMessage()
        )

    def SendWithCustomSenderReplyToAndCc(self):
        client = self.client
        return client.Messaging.Email.SendMessage(
            EmailSubject="Test Email",
            MessagePlain="Hi world!",
            Destination="recipient@example.com",
            From="Support Team",
            FromEmail="support@example.com",
            ReplyTo="replies@example.com",
            CCEmail="manager@example.com",
        )

    def Status(self, MessageID: str):
        client = self.client
        return client.Messaging.Email.Status(MessageID, RecordsPerPage=20, Page=1)

    def Reschedule(self, MessageID: str):
        client = self.client
        return client.Messaging.Email.Reschedule(MessageID, SendTime="2026-08-01T09:00:00")

    def Abort(self, MessageID: str):
        client = self.client
        return client.Messaging.Email.Abort(MessageID)

    def Resubmit(self, MessageID: str):
        client = self.client
        return client.Messaging.Email.Resubmit(MessageID, SendTime="2026-08-01T09:00:00")
