from dataclasses import dataclass, field
from datetime import datetime

from tnzapi.helpers.functions import Functions


@dataclass
class GroupModel:
    
    GroupCode: str = None
    GroupName: str = None
    SubAccount: str = None
    Department: str = None
    ViewEditBy: str = None
    Owner: str = None

    def __repr__(self):
        return Functions.__pretty_class__(self, self)