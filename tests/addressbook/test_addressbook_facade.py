from tnzapi.api.v300.addressbook import Addressbook
from tnzapi.api.v300.addressbook.builders.contact import Contact
from tnzapi.api.v300.addressbook.builders.group import Group
from tnzapi.api.v300.addressbook.builders.contact_group import ContactGroup
from tnzapi.api.v300.addressbook.builders.group_contact import GroupContact


def test_addressbook_exposes_contact(api_user):
    addressbook = Addressbook(api_user)
    assert isinstance(addressbook.Contact, Contact)


def test_addressbook_exposes_group(api_user):
    addressbook = Addressbook(api_user)
    assert isinstance(addressbook.Group, Group)


def test_addressbook_exposes_contact_group(api_user):
    addressbook = Addressbook(api_user)
    assert isinstance(addressbook.ContactGroup, ContactGroup)


def test_addressbook_exposes_group_contact(api_user):
    addressbook = Addressbook(api_user)
    assert isinstance(addressbook.GroupContact, GroupContact)
