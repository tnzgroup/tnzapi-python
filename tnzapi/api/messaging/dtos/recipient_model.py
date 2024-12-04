from dataclasses import dataclass, field

from tnzapi.helpers.functions import Functions


@dataclass
class RecipientModel:
    
    Recipient: str = None

    Company: str = None
    Attention: str = None
    FirstName: str = None
    LastName: str = None

    Custom1: str = None
    Custom2: str = None
    Custom3: str = None
    Custom4: str = None
    Custom5: str = None
    Custom6: str = None
    Custom7: str = None
    Custom8: str = None
    Custom9: str = None

    ContactID: str = None
    GroupID: str = None

    MobileNumber: str = None
    FaxNumber: str = None
    PhoneNumber: str = None
    EmailAddress: str = None    

    def __repr__(self):
        return Functions.__pretty_class__(self, self)