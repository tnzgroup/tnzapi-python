from dataclasses import dataclass, field

from tnzapi.helpers.functions import Functions


@dataclass
class ContactGroupApiCreateRequestDTO:
    
    GroupCode: str = None

    def __repr__(self):
        return Functions.__pretty_class__(self, self)