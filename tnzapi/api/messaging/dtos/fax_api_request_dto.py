from dataclasses import dataclass, field
from datetime import datetime

from tnzapi.api.messaging.dtos.common_api_request_dto import CommonApiRequestDTO
from tnzapi.helpers.functions import Functions

@dataclass
class FaxApiRequestDTO(CommonApiRequestDTO):
    Resolution: str = None
    CSID: str = None
    StampFormat: str = None
    WatermarkFolder: str = None
    WatermarkFirstPage: str = None
    WatermarkAllPages: str = None
    RetryAttempts: int = 3
    RetryPeriod: str = 1
    Message: str = None
    Files: list[str] = field(default_factory=list)

    def __repr__(self):
        return Functions.__pretty_class__(self, self)
