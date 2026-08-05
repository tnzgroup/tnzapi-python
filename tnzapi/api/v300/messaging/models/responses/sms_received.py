from dataclasses import dataclass, field


@dataclass
class SMSReceived:
    """Minimal stub for the /sms/received response shape.

    Fleshed out fully in Phase 4 (Reports) - kept minimal here since Phase 1
    only needs SMS.Received() to exist and round-trip a mocked response.
    """
    Result: str = None
    TotalRecords: int = None
    RecordsPerPage: int = None
    PageCount: int = None
    Page: int = None
    Messages: list = field(default_factory=list)
    ErrorMessage: list = field(default_factory=list)


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"SMSReceivedDTO": SMSReceived})

__all__ = ["SMSReceived", "SMSReceivedDTO"]
