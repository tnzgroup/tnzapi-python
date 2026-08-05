from dataclasses import dataclass, field


@dataclass
class ContactResponse:
    Result: str = None
    ErrorMessage: list = field(default_factory=list)
    ContactID: str = None
    Owner: str = None
    CreatedTimeLocal: str = None
    CreatedTimeUTC: str = None
    CreatedTimeUTC_RFC3339: str = None
    UpdatedTimeLocal: str = None
    UpdatedTimeUTC: str = None
    UpdatedTimeUTC_RFC3339: str = None
    Timezone: str = None
    Groups: list = field(default_factory=list)
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

__getattr__ = deprecated_alias({"ContactResponseDTO": ContactResponse})

__all__ = ["ContactResponse", "ContactResponseDTO"]
