from dataclasses import dataclass, field

from tnzapi.api.messaging.dtos.common_api_request_dto import CommonApiRequestDTO
from tnzapi.core.messaging import Keypad
from tnzapi.helpers.functions import Functions

@dataclass
class TTSApiRequestDTO(CommonApiRequestDTO):
    CallerID: str = None
    BillingAccount: str = None
    ReportTo: str = None
    RetryAttempts: int = 1
    RetryPeriod: int = 1
    MessageToPeople: str = None
    MessageToAnswerphones: str = None
    CallRouteMessageToPeople: str = None
    CallRouteMessageToOperators: str = None
    CallRouteMessageOnWrongKey: str = None
    NumberOfOperators: int = 0
    Voice: str = "English-NewZealand@Female1"
    Options: str = None
    Keypads: list[Keypad] = field(default_factory=list)

    def __repr__(self):
        return Functions.__pretty_class__(self, self)
    
