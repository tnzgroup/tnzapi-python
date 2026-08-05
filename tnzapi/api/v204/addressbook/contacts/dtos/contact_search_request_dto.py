from dataclasses import dataclass, field

from tnzapi.helpers.functions import Functions


@dataclass
class ContactSearchRequestDTO:
    EmailAddress: str = ""
    MobilePhone: str = ""
    MainPhone: str = ""
    Attention: str = ""
    FirstName: str = ""
    LastName: str = ""
    Company: str = ""

    Page: int = 1
    RecordsPerPage: int = 100

    def __repr__(self):
        return Functions.__pretty_class__(self, self)