from dataclasses import dataclass
from typing import Optional

from tnzapi.core.dict_compat import DictCompatMixin


@dataclass
class SMSReply(DictCompatMixin):
    ReceivedID: Optional[str] = None
    ReceivedTimeLocal: Optional[str] = None
    ReceivedTimeUTC: Optional[str] = None
    ReceivedTimeUTC_RFC3339: Optional[str] = None
    Timezone: Optional[str] = None
    From: Optional[str] = None
    MessageText: Optional[str] = None

    # _extras (any raw dict key not in this dataclass's own schema, preserved by
    # convert_list_field() so it's still reachable via DictCompatMixin's dict-style
    # access) is deliberately NOT declared as a dataclass field here - dataclasses.
    # asdict() has no way to skip a declared field, so it would leak straight into
    # any asdict()-based serialization forever. It's attached as a plain instance
    # attribute after construction instead (see convert_list_field), which
    # DictCompatMixin already reads defensively via getattr(self, "_extras", None).


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"SMSReplyDTO": SMSReply})

__all__ = ["SMSReply", "SMSReplyDTO"]
