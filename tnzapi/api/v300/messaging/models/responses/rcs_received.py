from dataclasses import dataclass, field


@dataclass
class RCSReceived:
    Result: str = None
    TotalRecords: int = None
    RecordsPerPage: int = None
    PageCount: int = None
    Page: int = None
    Messages: list = field(default_factory=list)
    ErrorMessage: list = field(default_factory=list)


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"RCSReceivedDTO": RCSReceived})

__all__ = ["RCSReceived", "RCSReceivedDTO"]
