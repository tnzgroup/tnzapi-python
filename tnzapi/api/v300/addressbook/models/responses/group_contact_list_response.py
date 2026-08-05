from dataclasses import dataclass, field


@dataclass
class GroupContactListResponse:
    Result: str = None
    ErrorMessage: list = field(default_factory=list)
    TotalRecords: int = None
    RecordsPerPage: int = None
    PageCount: int = None
    Page: int = None
    Group: dict = None
    Contacts: list = field(default_factory=list)


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"GroupContactListResponseDTO": GroupContactListResponse})

__all__ = ["GroupContactListResponse", "GroupContactListResponseDTO"]
