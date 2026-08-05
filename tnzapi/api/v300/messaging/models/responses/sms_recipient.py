from dataclasses import dataclass, field
from typing import Optional

from tnzapi.core.dict_compat import DictCompatMixin
from tnzapi.core.model_conversion import TypedListFieldMixin
from tnzapi.api.v300.messaging.models.responses.sms_reply import SMSReply


@dataclass
class SMSRecipient(DictCompatMixin, TypedListFieldMixin):
    Type: Optional[str] = None
    DestSeq: Optional[str] = None
    Destination: Optional[str] = None
    ContactID: Optional[str] = None
    Status: Optional[str] = None
    Result: Optional[str] = None
    MessageText: Optional[str] = None
    SentTimeLocal: Optional[str] = None
    SentTimeUTC: Optional[str] = None
    SentTimeUTC_RFC3339: Optional[str] = None
    Attention: Optional[str] = None
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
    RemoteID: Optional[str] = None
    Price: Optional[str] = None
    SMSReplies: "list[SMSReply]" = field(default_factory=list)

    # See SMSReply's own comment — _extras is deliberately NOT a declared
    # dataclass field (dataclasses.asdict() can't skip a declared field, so it
    # would leak into serialization forever); it's attached as a plain instance
    # attribute after construction by convert_list_field() instead.

    # Unannotated on purpose — see TypedListFieldMixin's docstring for why a
    # ClassVar annotation must never go directly on a @dataclass body like this one.
    _TYPED_LIST_FIELDS = {"SMSReplies": SMSReply}

from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"SMSRecipientDTO": SMSRecipient})

__all__ = ["SMSRecipient", "SMSRecipientDTO"]
