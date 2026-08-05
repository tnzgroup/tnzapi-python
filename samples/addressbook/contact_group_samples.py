"""Contact<->Group membership, viewed from the contact's side.

Full field reference: README.md > Addressbook > Contact Groups.
"""

from tnzapi import TNZAPI


class ContactGroupSamples:

    def __init__(self, client: TNZAPI = None):
        self.client = client or TNZAPI()

    def AddToGroup(self, ContactID: str, GroupID: str):
        client = self.client
        return client.Addressbook.ContactGroup.Create(ContactID, GroupID)

    def RemoveFromGroup(self, ContactID: str, GroupID: str):
        client = self.client
        return client.Addressbook.ContactGroup.Delete(ContactID, GroupID)

    def Details(self, ContactID: str, GroupID: str):
        client = self.client
        return client.Addressbook.ContactGroup.Detail(ContactID, GroupID)

    def ListGroupsForContact(self, ContactID: str):
        client = self.client
        return client.Addressbook.ContactGroup.List(ContactID, RecordsPerPage=10, Page=1)
