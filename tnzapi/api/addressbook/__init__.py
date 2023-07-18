class Addressbook(object):
    
    def __init__(self):
        self._contact = None
        self._contact_group = None
        self._group = None
        self._group_contact = None

    #
    # Contact
    #
    @property
    def Contact(self, **kwargs):
        
        from tnzapi.api.addressbook.contacts.requests import Contact as contact
        
        if self._contact != None:
            del(self._contact)

        self._contact = contact(**kwargs)

        return self._contact
    
    #
    # Contact Group
    #
    @property
    def ContactGroup(self, **kwargs):
        
        from tnzapi.api.addressbook.contactgroups.requests import ContactGroup as contact_group
        
        if self._contact_group != None:
            del(self._contact_group)

        self._contact_group = contact_group(**kwargs)

        return self._contact_group

    #
    # Group
    #
    @property
    def Group(self, **kwargs):
        
        from tnzapi.api.addressbook.groups.requests import Group as group

        if self._group != None:
            del(self._group)

        self._group = group(**kwargs)

        return self._group

    #
    # Group Contact
    #
    @property
    def GroupContact(self, **kwargs):
        
        from tnzapi.api.addressbook.groupcontacts.requests import GroupContact as group_contact
        
        if self._group_contact != None:
            del(self._group_contact)

        self._group_contact = group_contact(**kwargs)

        return self._group_contact