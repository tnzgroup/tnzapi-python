from dataclasses import dataclass, field


@dataclass
class ContactGroupListResponse:
    Result: str = None
    ErrorMessage: list = field(default_factory=list)
    TotalRecords: int = None
    RecordsPerPage: int = None
    PageCount: int = None
    Page: int = None
    Contact: dict = None
    Groups: list = field(default_factory=list)


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"ContactGroupListResponseDTO": ContactGroupListResponse})

__all__ = ["ContactGroupListResponse", "ContactGroupListResponseDTO"]
