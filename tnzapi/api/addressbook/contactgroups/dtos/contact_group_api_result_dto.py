from dataclasses import dataclass, field

from tnzapi.api.addressbook.contacts.dtos.contact_model import ContactModel
from tnzapi.api.addressbook.groups.dtos.group_model import GroupModel


from tnzapi.helpers.functions import Functions


@dataclass
class ContactGroupApiResultDTO:
    
    Result: str = None
    Contact: ContactModel = None
    Group: GroupModel = None
    ErrorMessage: list[str] = field(default_factory=list)

    def __repr__(self):
        return Functions.__pretty_class__(self, self)