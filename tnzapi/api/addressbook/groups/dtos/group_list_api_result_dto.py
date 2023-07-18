from dataclasses import dataclass, field

from tnzapi.api.addressbook.groups.dtos.group_model import GroupModel
from tnzapi.helpers.functions import Functions

@dataclass
class GroupListApiResultDTO:
    
    Result: str = None
    TotalRecords: int = 0
    RecordsPerPage: int = 100
    PageCount: int = 0
    Page: int = 1
    Groups: list[GroupModel] = field(default_factory=list)
    ErrorMessage: list[str] = field(default_factory=list)

    def __repr__(self):
        return Functions.__pretty_class__(self, self)