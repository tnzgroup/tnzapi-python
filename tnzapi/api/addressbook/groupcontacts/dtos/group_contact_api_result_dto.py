from dataclasses import dataclass, field

from tnzapi.api.addressbook.contacts.dtos.contact_model import ContactModel
from tnzapi.api.addressbook.groups.dtos.group_model import GroupModel


from tnzapi.helpers.functions import Functions


@dataclass
class GroupContactApiResultDTO:
    
    Result: str = None
    Group: GroupModel = None
    Contact: ContactModel = None
    ErrorMessage: list[str] = field(default_factory=list)

    def __repr__(self):
        return Functions.__pretty_class__(self, self)