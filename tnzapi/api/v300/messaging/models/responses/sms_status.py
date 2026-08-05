from dataclasses import dataclass, field

from tnzapi.core.model_conversion import TypedListFieldMixin
from tnzapi.core.serialization import ToDictMixin
from tnzapi.api.v300.messaging.models.responses.sms_recipient import SMSRecipient


@dataclass
class SMSStatus(ToDictMixin, TypedListFieldMixin):
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
    Recipients: "list[SMSRecipient]" = field(default_factory=list)
    ErrorMessage: list = field(default_factory=list)

    # Unannotated on purpose — see TypedListFieldMixin's docstring for why a
    # ClassVar annotation must never go directly on a @dataclass body like this one.
    _TYPED_LIST_FIELDS = {"Recipients": SMSRecipient}

from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"SMSStatusDTO": SMSStatus})

__all__ = ["SMSStatus", "SMSStatusDTO"]
