"""Addressbook Group sample code. Full field reference: README.md > Addressbook > Groups."""

from tnzapi import TNZAPI


class GroupSamples:

    def __init__(self, client: TNZAPI = None):
        self.client = client or TNZAPI()

    def List(self):
        client = self.client
        return client.Addressbook.Group.List(RecordsPerPage=10, Page=1)

    def Details(self, GroupID: str):
        client = self.client
        return client.Addressbook.Group.Detail(GroupID)

    def Create(self):
        client = self.client
        return client.Addressbook.Group.Create(GroupName="[Group Name]")

    def Update(self, GroupID: str):
        client = self.client
        return client.Addressbook.Group.Update(GroupID, GroupName="[New Group Name]")

    def Delete(self, GroupID: str):
        client = self.client
        return client.Addressbook.Group.Delete(GroupID)

    def FullGroupLifecycle(self):
        """Recipe: create a group, create a contact, add it to the group, list
        members, remove it, then clean up both records."""
        client = self.client

        group = client.Addressbook.Group.Create(GroupName="Demo Group")
        if group.Result != "Success":
            print("Group creation failed:", group.ErrorMessage)
            return

        group_id = group.GroupID
        print("Created group:", group_id)

        contact = client.Addressbook.Contact.Create(
            FirstName="Demo",
            LastName="User",
            MobilePhone="+6421000001"
        )
        if contact.Result != "Success":
            print("Contact creation failed:", contact.ErrorMessage)
            client.Addressbook.Group.Delete(group_id)
            return

        contact_id = contact.ContactID
        print("Created contact:", contact_id)

        client.Addressbook.GroupContact.Create(group_id, contact_id)
        print("Added contact to group")

        members = client.Addressbook.GroupContact.List(group_id)
        if members.Result == "Success":
            print("Group members:", members.TotalRecords)

        client.Addressbook.GroupContact.Delete(group_id, contact_id)
        print("Removed contact from group")

        client.Addressbook.Contact.Delete(contact_id)
        client.Addressbook.Group.Delete(group_id)
        print("Cleanup complete")
