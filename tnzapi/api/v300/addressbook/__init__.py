class Addressbook:

    def __init__(self, user):
        self.user = user

    @property
    def Contact(self):
        from tnzapi.api.v300.addressbook.builders.contact import Contact
        return Contact(self.user)

    @property
    def Group(self):
        from tnzapi.api.v300.addressbook.builders.group import Group
        return Group(self.user)

    @property
    def ContactGroup(self):
        from tnzapi.api.v300.addressbook.builders.contact_group import ContactGroup
        return ContactGroup(self.user)

    @property
    def GroupContact(self):
        from tnzapi.api.v300.addressbook.builders.group_contact import GroupContact
        return GroupContact(self.user)
