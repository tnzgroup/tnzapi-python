"""Fax sample code. Full field reference: README.md > Messaging > Fax."""

from tnzapi import TNZAPI
from tnzapi.core.destination import Destination
from tnzapi.core.file_attachment import FileAttachment
from tnzapi.core.send_mode import SendMode


class FaxSamples:

    def __init__(self, client: TNZAPI = None):
        self.client = client or TNZAPI()

    def Send(self):
        client = self.client
        return client.Messaging.Fax.SendMessage(
            Destination="+6491232345",
            Files=[{"Name": "Document.pdf", "Data": "<base64-encoded file data>"}]
        )

    def SendInTestMode(self):
        """Mode=SendMode.Test validates the send without actually delivering
        it - equivalent to Mode="Test"."""
        client = self.client
        return (
            client.Messaging.Fax
            .Set(
                Mode=SendMode.Test  # Test mode
            )
            .AddDestination("+6491232345")
            .AddAttachment("path/to/doc.pdf")
            .SendMessage()
        )

    def SendUsingBuilder(self):
        client = self.client
        return (
            client.Messaging.Fax
            .Set()
            .AddDestination("+6491232345")
            .AddAttachment("path/to/doc.pdf")
            .SendMessage()
        )

    def SendUsingAddDestinations(self):
        """AddDestinations([...]) adds several destinations in one call - each
        item can be a bare string, a dict, or a typed Destination, mixed
        freely. AddDestination(...) (singular) only ever adds one and raises
        TypeError if given a list directly."""
        client = self.client
        return (
            client.Messaging.Fax
            .Set()
            .AddAttachment("path/to/doc.pdf")
            .AddDestinations(["+6491232345", "+6491232346"])
            .SendMessage()
        )

    def SendUsingAddAttachments(self):
        """AddAttachments([...]) adds several attachments (e.g. multiple pages
        sent as separate files) in one call - each item can be a path string,
        a dict, or a FileAttachment instance."""
        client = self.client
        return (
            client.Messaging.Fax
            .Set()
            .AddDestination("+6491232345")
            .AddAttachments(["path/to/page1.pdf", "path/to/page2.pdf"])
            .SendMessage()
        )

    def SendFromFilePath(self, FilePath: str = "path/to/doc.pdf"):
        client = self.client
        return (
            client.Messaging.Fax
            .Set()
            .AddDestination("+6491232345")
            .AddAttachment(FilePath)
            .SendMessage()
        )

    def SendUsingTypedFileAttachment(self, FilePath: str = "path/to/doc.pdf"):
        """FileAttachment(FilePath) is equivalent to AddAttachment(FilePath)
        above - useful when you want to build the attachment separately from
        the AddAttachment(...) call, e.g. to reuse it across multiple sends."""
        client = self.client
        return (
            client.Messaging.Fax
            .Set()
            .AddDestination("+6491232345")
            .AddAttachment(
                FileAttachment(FilePath)
            )
            .SendMessage()
        )

    def SendWithReferenceFields(self):
        """Fax has no message body, so Company/Attention/Custom1-9 on a
        destination are never rendered into anything - but they're still
        accepted and echoed back in status reports, for your own reference."""
        client = self.client
        return client.Messaging.Fax.SendMessage(
            Destinations=[
                Destination(
                    FaxNumber="+6491232345",
                    Attention="Accounts Payable",
                    Custom1="Invoice #1234",
                ),
            ],
            Files=[{"Name": "Invoice.pdf", "Data": "<base64-encoded file data>"}],
        )

    def SendWithReferenceFieldsUsingAddDestinations(self):
        """Fax has no message body, so Company/Attention/Custom1-9 on a
        destination are never rendered into anything - but they're still
        accepted and echoed back in status reports, for your own reference.
        AddDestinations([...]) adds several destinations in one call."""
        client = self.client
        return (
            client.Messaging.Fax
            .Set()
            .AddAttachment("path/to/doc.pdf")
            .AddDestinations([
                Destination(
                    FaxNumber="+6491232345",
                    Attention="Accounts Payable",
                    Custom1="Invoice #1234",
                ),
                Destination(
                    FaxNumber="+6491232346",
                    Attention="Purchasing",
                    Custom1="Invoice #1235",
                ),
            ])
            .SendMessage()
        )

    def SendUsingAddressbookDestination(self):
        client = self.client
        return (
            client.Messaging.Fax
            .Set()
            .AddAttachment("path/to/doc.pdf")
            .AddDestination(ContactID="[Contact ID]")
            .AddDestination(GroupID="[Group ID]")
            .SendMessage()
        )

    def SendToMultipleRecipients(self):
        client = self.client
        return client.Messaging.Fax.SendMessage(
            Destinations=[
                {"ToNumber": "+6491232345"},
                {"ToNumber": "+6491232346"}
            ],
            Files=[{"Name": "Document.pdf", "Data": "<base64-encoded file data>"}]
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
        return client.Messaging.Fax.SendMessage(
            Files=[{"Name": "Document.pdf", "Data": "<base64-encoded file data>"}],
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
            client.Messaging.Fax
            .Set()
            .AddAttachment("path/to/doc.pdf")
            .AddDestination(ContactID="[Contact ID 1]")
            .AddDestination(ContactID="[Contact ID 2]")
            .AddDestination(GroupID="[Group ID 1]")
            .AddDestination(GroupID="[Group ID 2]")
            .SendMessage()
        )

    def SendScheduled(self):
        client = self.client
        return client.Messaging.Fax.SendMessage(
            Destination="+6491232345",
            Files=[{"Name": "Document.pdf", "Data": "<base64-encoded file data>"}],
            SendTime="2026-08-01T09:00:00",
            Timezone="Pacific/Auckland"
        )

    def SendWithCSIDResolutionRetryAndWatermark(self):
        client = self.client
        return client.Messaging.Fax.SendMessage(
            Destination="+6491232345",
            Files=[{"Name": "Document.pdf", "Data": "<base64-encoded file data>"}],
            CSID="TNZ Group",
            Resolution="Fine",
            RetryAttempts=3,
            RetryPeriod=15,
            WatermarkFolder="Invoices",
            WatermarkFirstPage="CONFIDENTIAL",
            WatermarkAllPages="Page [[PageNumber]]"
        )

    def Status(self, MessageID: str):
        client = self.client
        return client.Messaging.Fax.Status(MessageID, RecordsPerPage=20, Page=1)

    def Reschedule(self, MessageID: str):
        client = self.client
        return client.Messaging.Fax.Reschedule(MessageID, SendTime="2026-08-01T09:00:00")

    def Abort(self, MessageID: str):
        client = self.client
        return client.Messaging.Fax.Abort(MessageID)

    def Resubmit(self, MessageID: str):
        client = self.client
        return client.Messaging.Fax.Resubmit(MessageID, SendTime="2026-08-01T09:00:00")
