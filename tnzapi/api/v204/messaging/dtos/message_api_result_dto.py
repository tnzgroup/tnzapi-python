from dataclasses import dataclass, field

from tnzapi.helpers.functions import Functions

@dataclass
class MessageApiResultDTO:
    Result: str = None
    MessageID: str = None
    ErrorMessage: list[str] = field(default_factory=list)

    def __repr__(self):
        return Functions.__pretty_class__(self, self)