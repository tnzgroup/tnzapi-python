from dataclasses import dataclass, field


@dataclass
class OptOutResponse:
    Result: str = None
    ErrorMessage: list = field(default_factory=list)
    ID: str = None
    DestType: str = None
    Destination: str = None
    ContactID: str = None
    SubAccount: str = None
    Department: str = None
    StopMessage: str = None
    Notes: str = None
    OriginalMessage: str = None
    CreatedTimeLocal: str = None
    CreatedTimeUTC: str = None
    CreatedTimeUTC_RFC3339: str = None
    UpdatedTimeLocal: str = None
    UpdatedTimeUTC: str = None
    UpdatedTimeUTC_RFC3339: str = None
    Timezone: str = None


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"OptOutResponseDTO": OptOutResponse})

__all__ = ["OptOutResponse", "OptOutResponseDTO"]