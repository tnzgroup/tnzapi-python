from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class Destination:
    Recipient: Optional[str] = None
    ToNumber: Optional[str] = None
    MobilePhone: Optional[str] = None
    MainPhone: Optional[str] = None
    FaxNumber: Optional[str] = None
    EmailAddress: Optional[str] = None
    ContactID: Optional[str] = None
    GroupID: Optional[str] = None
    GroupCode: Optional[str] = None
    Attention: Optional[str] = None
    FirstName: Optional[str] = None
    LastName: Optional[str] = None
    Company: Optional[str] = None
    Custom1: Optional[str] = None
    Custom2: Optional[str] = None
    Custom3: Optional[str] = None
    Custom4: Optional[str] = None
    Custom5: Optional[str] = None
    Custom6: Optional[str] = None
    Custom7: Optional[str] = None
    Custom8: Optional[str] = None
    Custom9: Optional[str] = None


def normalize_destination(value, primary_key: Optional[str] = None):
    """Validates and normalizes a single destination value into a plain dict
    ready to append to a Destinations list. `primary_key` is the field a bare
    string shorthand maps to (e.g. "ToNumber" for most channels, "EmailAddress"
    for Email). Returns None if `value` doesn't represent a destination (e.g.
    None was passed). Raises ValueError on an unknown dict key.
    """
    if isinstance(value, Destination):
        return {k: v for k, v in asdict(value).items() if v is not None} or None
    if isinstance(value, dict):
        invalid = next((k for k in value if k not in Destination.__dataclass_fields__), None)
        if invalid:
            raise ValueError(f"Unknown destination field: {invalid}")
        return value
    if isinstance(value, str):
        return {primary_key: value}
    return None
