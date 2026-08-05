from dataclasses import dataclass, field


@dataclass
class WhatsAppStatus:
    Result: str = None
    MessageID: str = None
    JobStatus: str = None
    JobNum: str = None
    Account: str = None
    SubAccount: str = None
    Department: str = None
    Reference: str = None
    CreatedTimeLocal: str = None
    CreatedTimeUTC: str = None
    CreatedTimeUTC_RFC3339: str = None
    DelayedTimeLocal: str = None
    DelayedTimeUTC: str = None
    DelayedTimeUTC_RFC3339: str = None
    Timezone: str = None
    Count: int = None
    Complete: int = None
    Success: int = None
    Failed: int = None
    Price: str = None
    TotalRecords: int = None
    RecordsPerPage: int = None
    PageCount: int = None
    Page: int = None
    Recipients: list = field(default_factory=list)
    ErrorMessage: list = field(default_factory=list)


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"WhatsAppStatusDTO": WhatsAppStatus})

__all__ = ["WhatsAppStatus", "WhatsAppStatusDTO"]
