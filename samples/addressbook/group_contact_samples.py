"""Contact<->Group membership, viewed from the group's side (symmetric counterpart
to ContactGroupSamples). Full field reference: README.md > Addressbook > Group Contacts.
"""

from tnzapi import TNZAPI


class GroupContactSamples:

    def __init__(self, client: TNZAPI = None):
        self.client = client or TNZAPI()

    def AddContact(self, GroupID: str, ContactID: str):
        client = self.client
        return client.Addressbook.GroupContact.Create(GroupID, ContactID)

    def RemoveContact(self, GroupID: str, ContactID: str):
        client = self.client
        return client.Addressbook.GroupContact.Delete(GroupID, ContactID)

    def Details(self, GroupID: str, ContactID: str):
        client = self.client
        return client.Addressbook.GroupContact.Detail(GroupID, ContactID)

    def ListContactsInGroup(self, GroupID: str):
        client = self.client
        return client.Addressbook.GroupContact.List(GroupID, RecordsPerPage=10, Page=1)
