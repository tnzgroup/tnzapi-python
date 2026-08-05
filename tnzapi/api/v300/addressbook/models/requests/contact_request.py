from dataclasses import dataclass


@dataclass
class ContactRequest:
    ExType: str = None
    ExID: str = None
    ViewBy: str = None
    EditBy: str = None
    AccessControl: str = None
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
    Postcode: str = None
    MainPhone: str = None
    AltPhone1: str = None
    AltPhone2: str = None
    AltPhone3: str = None
    AltPhone4: str = None
    AltPhone5: str = None
    AltPhone6: str = None
    AltPhone7: str = None
    AltPhone8: str = None
    MobilePhone: str = None
    FaxNumber: str = None
    EmailAddress: str = None
    WebAddress: str = None
    Custom1: str = None
    Custom2: str = None
    Custom3: str = None
    Custom4: str = None
    Notes: str = None


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"ContactRequestDTO": ContactRequest})

__all__ = ["ContactRequest", "ContactRequestDTO"]
