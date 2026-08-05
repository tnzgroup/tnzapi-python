"""Workflow sample code. Full field reference: README.md > Messaging > Workflow.

Workflow requires a WorkflowTemplateID - the send is driven entirely by the
template configured against your account. Workflow has no Status/Received/
Actions - send only.
"""

from tnzapi import TNZAPI
from tnzapi.core.destination import Destination


class WorkflowSamples:

    def __init__(self, client: TNZAPI = None):
        self.client = client or TNZAPI()

    def Send(self):
        client = self.client
        return client.Messaging.Workflow.SendMessage(
            WorkflowTemplateID="[Your Workflow Template ID]",
            Destination="+64211234567"
        )

    def SendUsingBuilder(self):
        client = self.client
        return (
            client.Messaging.Workflow
            .Set(
                WorkflowTemplateID="[Your Workflow Template ID]"
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
            client.Messaging.Workflow
            .Set(WorkflowTemplateID="[Your Workflow Template ID]")
            .AddDestinations(["+64211234567", "+64211234568"])
            .SendMessage()
        )

    def SendWithPersonalisationUsingTypedDestination(self):
        """Personalisation fields on each destination are passed through to
        whichever channel(s) the Workflow Template actually routes to."""
        client = self.client
        return (
            client.Messaging.Workflow
            .Set(WorkflowTemplateID="[Your Workflow Template ID]")
            .AddDestinations([
                Destination(
                    ToNumber="+64211234567",
                    FirstName="Alice",
                    Company="Example Company",
                ),
                Destination(
                    ToNumber="+64211234568",
                    FirstName="Bob",
                    Company="Example Company",
                ),
            ])
            .SendMessage()
        )

    def SendUsingAddressbookDestination(self):
        client = self.client
        return (
            client.Messaging.Workflow
            .Set(
                WorkflowTemplateID="[Your Workflow Template ID]"
            )
            .AddDestination(ContactID="[Contact ID]")
            .AddDestination(GroupID="[Group ID]")
            .SendMessage()
        )

    def SendToMultipleRecipients(self):
        client = self.client
        return client.Messaging.Workflow.SendMessage(
            WorkflowTemplateID="[Your Workflow Template ID]",
            Destinations=[
                {"ToNumber": "+64211234567"},
                {"ToNumber": "+64211234568"}
            ]
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
        return client.Messaging.Workflow.SendMessage(
            WorkflowTemplateID="[Your Workflow Template ID]",
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
            client.Messaging.Workflow
            .Set(
                WorkflowTemplateID="[Your Workflow Template ID]"
            )
            .AddDestination(ContactID="[Contact ID 1]")
            .AddDestination(ContactID="[Contact ID 2]")
            .AddDestination(GroupID="[Group ID 1]")
            .AddDestination(GroupID="[Group ID 2]")
            .SendMessage()
        )

    def SendScheduled(self):
        client = self.client
        return client.Messaging.Workflow.SendMessage(
            WorkflowTemplateID="[Your Workflow Template ID]",
            Destination="+64211234567",
            SendTime="2026-08-01T09:00:00",
            Timezone="Pacific/Auckland"
        )

    def SendToNewContact(self):
        """If a destination isn't a known ContactID/GroupID, the API
        automatically creates (or updates) an Addressbook contact from the
        fields you supply alongside it."""
        client = self.client
        return client.Messaging.Workflow.SendMessage(
            WorkflowTemplateID="[Your Workflow Template ID]",
            Destinations=[{
                "ToNumber": "+6421000001",
                "EmailAddress": "john.doe@example.com",
                "MainPhone": "+6421000001",
                "Attention": "John Doe",
                "FirstName": "John",
                "LastName": "Doe",
                "Company": "Example Company"
            }]
        )
