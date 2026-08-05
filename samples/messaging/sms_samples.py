"""SMS sample code. Full field reference: README.md > Messaging > SMS."""

from tnzapi import TNZAPI
from tnzapi.core.destination import Destination
from tnzapi.core.send_mode import SendMode

from samples.messaging._pagination import WalkAllPages


class SMSSamples:

    def __init__(self, client: TNZAPI = None):
        self.client = client or TNZAPI()

    def Send(self):
        """Flat kwargs - every field passed to SendMessage() in one call."""
        client = self.client
        return client.Messaging.SMS.SendMessage(
            Message="Test SMS Message click [[Reply]] to opt out",
            Destination="+64211231234",
            Reference="Test"
        )

    def SendInTestMode(self):
        """Mode=SendMode.Test validates the send without actually delivering
        it - equivalent to Mode="Test"."""
        client = self.client
        return (
            client.Messaging.SMS
            .Set(
                Message="Test SMS Message click [[Reply]] to opt out",
                Mode=SendMode.Test  # Test mode
            )
            .AddDestination("+64211231234")
            .SendMessage()
        )

    def SendUsingBuilder(self):
        """Builder style - Set()/AddDestination() chained, finished with SendMessage()."""
        client = self.client
        return (
            client.Messaging.SMS
            .Set(
                Message="Test SMS Message click [[Reply]] to opt out",
                Reference="Test"
            )
            .AddDestination("+64211231234")
            .SendMessage()
        )

    def SendUsingAddDestinations(self):
        """AddDestinations([...]) adds several destinations in one call - each
        item can be a bare string, a dict, or a typed Destination, mixed
        freely. AddDestination(...) (singular) only ever adds one and raises
        TypeError if given a list directly."""
        client = self.client
        return (
            client.Messaging.SMS
            .Set(Message="Hi [[FirstName]]!")
            .AddDestinations([
                "+64211231234",
                {"ToNumber": "+64211231235", "FirstName": "Alice"},
            ])
            .SendMessage()
        )

    def SendUsingAddAttachments(self):
        """AddAttachments([...]) adds several attachments in one call - each
        item can be a path string, a dict, or a FileAttachment instance."""
        client = self.client
        return (
            client.Messaging.SMS
            .Set(Message="Here's what you requested: [[File1]] [[File2]]")
            .AddDestination("+64211231234")
            .AddAttachments(["path/to/photo.jpg", "path/to/receipt.pdf"])
            .SendMessage()
        )

    def SendUsingAddressbookDestination(self):
        """AddDestination() also accepts a Contact/Group from your Addressbook."""
        client = self.client
        return (
            client.Messaging.SMS
            .Set(Message="Hi [[FirstName]], see you soon!")
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
        return client.Messaging.SMS.SendMessage(
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
            client.Messaging.SMS
            .Set(
                Message="Hi [[FirstName]]!"
            )
            .AddDestination(ContactID="[Contact ID 1]")
            .AddDestination(ContactID="[Contact ID 2]")
            .AddDestination(GroupID="[Group ID 1]")
            .AddDestination(GroupID="[Group ID 2]")
            .SendMessage()
        )

    def SendToMultipleGroupsAndContactsUsingTypedDestination(self):
        """Same idea as SendToMultipleContactsAndGroups(), but built from typed
        Destination instances instead of raw dicts - identical wire result,
        construction-time field validation instead of a runtime ValueError/
        Result="Failed" if a key is mistyped."""
        client = self.client
        return client.Messaging.SMS.SendMessage(
            Message="Reminder: your subscription renews tomorrow.",
            Destinations=[
                Destination(GroupID="[Group ID 1]"),
                Destination(GroupID="[Group ID 2]"),
                Destination(ContactID="[Contact ID 1]"),
                Destination(ContactID="[Contact ID 2]"),
            ],
        )

    def SendWithPersonalisationUsingTypedDestination(self):
        """Per-destination personalisation via typed Destination instances,
        builder style."""
        client = self.client
        return (
            client.Messaging.SMS
            .Set(
                Message="Hi [[FirstName]], your appointment is on [[Custom1]]."
            )
            .AddDestinations([
                Destination(
                    ToNumber="+64211231234",
                    FirstName="Alice",
                    Custom1="Monday 3pm",
                ),
                Destination(
                    ToNumber="+64211231235",
                    FirstName="Bob",
                    Custom1="Tuesday 10am",
                ),
            ])
            .SendMessage()
        )

    def SendFileViaMessageLink(self, FilePath: str = "path/to/photo.jpg"):
        """NZ carriers don't support MMS - attach a file with AddAttachment(...)
        (a file path is read and base64-encoded automatically), then reference
        it in the message text with [[File1]]; the recipient gets an SMS with
        a link to the file instead of an inline attachment."""
        client = self.client
        return (
            client.Messaging.SMS
            .Set(Message = "Here's the photo you requested: [[File1]]")
            .AddDestination("+64211231234")
            .AddAttachment(FilePath)
            .SendMessage()
        )

    def SendToMultipleRecipients(self):
        client = self.client
        return client.Messaging.SMS.SendMessage(
            Message="Test SMS Message click [[Reply]] to opt out",
            Destinations=[
                {"ToNumber": "+64211231234"},
                {"ToNumber": "+64211231235"}
            ],
            Reference="Test"
        )

    def SendScheduledWithWebhook(self):
        client = self.client
        return client.Messaging.SMS.SendMessage(
            Message="Test SMS Message click [[Reply]] to opt out",
            Destination="+64211231234",
            SendTime="2026-08-01T09:00:00",
            Timezone="Pacific/Auckland",
            WebhookCallbackURL="https://example.com/webhooks/tnz/result",
            WebhookCallbackFormat="JSON"
        )

    def Status(self, MessageID: str):
        client = self.client
        return client.Messaging.SMS.Status(MessageID, RecordsPerPage=20, Page=1)

    def Received(self):
        """Inbound SMS replies from the last 24 hours (TimePeriod is minutes, max 1440)."""
        client = self.client
        return client.Messaging.SMS.Received(TimePeriod=1440, RecordsPerPage=20, Page=1)

    def ReceivedByDateRange(self):
        client = self.client
        return client.Messaging.SMS.Received(
            DateFrom="2026-07-01 00:00:00",
            DateTo="2026-08-01 00:00:00",
            RecordsPerPage=20,
            Page=1
        )

    def GetAllInboundSMS(self, TimePeriodMinutes: int = 1440):
        """Walk every page - Received() only ever returns the requested page,
        it never auto-walks on your behalf."""
        client = self.client
        result = WalkAllPages(client.Messaging.SMS.Received, TimePeriodMinutes)
        if result.error:
            print("Walk stopped early:", result.error)
        print(f"Total inbound SMS in the last {TimePeriodMinutes} minutes: {len(result.messages)}")
        return result.messages

    def Reschedule(self, MessageID: str):
        client = self.client
        return client.Messaging.SMS.Reschedule(MessageID, SendTime="2026-08-01T09:00:00")

    def Abort(self, MessageID: str):
        client = self.client
        return client.Messaging.SMS.Abort(MessageID)
