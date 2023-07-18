from dataclasses import dataclass

from tnzapi.core.dtos.error_dto import ErrorDTO
from tnzapi.helpers.functions import Functions


@dataclass
class ErrorWithMessagIDDTO(ErrorDTO):
    MessageID: str = ""

    def __repr__(self):
        return Functions.__pretty_class__(self, self)