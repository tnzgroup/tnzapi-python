"""Addressbook Contact sample code. Full field reference: README.md > Addressbook > Contacts."""

from tnzapi import TNZAPI


class ContactSamples:

    def __init__(self, client: TNZAPI = None):
        self.client = client or TNZAPI()

    def List(self):
        """Only covers the requested page - inspect PageCount/TotalRecords to walk further pages yourself."""
        client = self.client
        return client.Addressbook.Contact.List(RecordsPerPage=10, Page=1)

    def Search(self):
        client = self.client
        return client.Addressbook.Contact.Search(Attention="Joe", RecordsPerPage=10, Page=1)

    def Details(self, ContactID: str):
        client = self.client
        return client.Addressbook.Contact.Detail(ContactID)

    def Create(self):
        client = self.client
        return client.Addressbook.Contact.Create(
            Title="Mr",
            Company="TNZ Group",
            FirstName="First",
            LastName="Last",
            MobilePhone="+642122223333"
        )

    def Update(self, ContactID: str):
        """Update is partial - only the fields you pass are changed."""
        client = self.client
        return client.Addressbook.Contact.Update(ContactID, Attention="Test Attention")

    def Delete(self, ContactID: str):
        client = self.client
        return client.Addressbook.Contact.Delete(ContactID)

    def FullCRUDLifecycle(self):
        """Recipe: Create -> Detail -> Update -> Delete in one flow."""
        client = self.client

        created = client.Addressbook.Contact.Create(
            FirstName="Test",
            LastName="User",
            MobilePhone="+6421000001",
            EmailAddress="test@example.com"
        )
        if created.Result != "Success":
            print("Create failed:", created.ErrorMessage)
            return

        contact_id = created.ContactID
        print("Created:", contact_id)

        detail = client.Addressbook.Contact.Detail(contact_id)
        if detail.Result == "Success":
            print("Read:", detail.FirstName, detail.LastName)

        client.Addressbook.Contact.Update(contact_id, Custom1="Updated")
        print("Updated custom field")

        client.Addressbook.Contact.Delete(contact_id)
        print("Deleted")
