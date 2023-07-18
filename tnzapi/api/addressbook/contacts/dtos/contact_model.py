from dataclasses import dataclass, field
from datetime import datetime

from tnzapi.helpers.functions import Functions


@dataclass
class ContactModel:
    
    ID: str = None
    Owner: str = None
    Created: datetime = None
    CreatedUTC: datetime = None
    Updated: datetime = None
    UpdatedUTC: datetime = None
    Timezone: datetime = None
    Attention: str = None
    Title: str = None
    Company: str = None
    RecipDepartment: str = None
    FirstName: str = None
    LastName: str = None
    Position: str = None
    StreetAddress: str = None
    Suburb: str = None
    City: str = None
    State: str = None
    Country: str = None
    PostCode: str = None
    MainPhone: str = None
    AltPhone1: str = None
    AltPhone2: str = None
    DirectPhone: str = None
    MobilePhone: str = None
    FaxNumber: str = None
    EmailAddress: str = None
    WebAddress: str = None
    Custom1: str = None
    Custom2: str = None
    Custom3: str = None
    Custom4: str = None
    ViewBy: str = None
    EditBy: str = None

    def __repr__(self):
        return Functions.__pretty_class__(self, self)