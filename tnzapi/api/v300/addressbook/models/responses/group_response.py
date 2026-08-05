from dataclasses import dataclass, field


@dataclass
class GroupResponse:
    Result: str = None
    ErrorMessage: list = field(default_factory=list)
    GroupID: str = None
    GroupCode: str = None
    Owner: str = None
    CreatedTimeLocal: str = None
    CreatedTimeUTC: str = None
    CreatedTimeUTC_RFC3339: str = None
    Timezone: str = None
    GroupName: str = None
    SubAccount: str = None
    Department: str = None
    ViewEditBy: str = None
    AccessControl: str = None


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"GroupResponseDTO": GroupResponse})

__all__ = ["GroupResponse", "GroupResponseDTO"]
