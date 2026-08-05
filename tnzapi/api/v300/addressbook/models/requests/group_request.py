from dataclasses import dataclass


@dataclass
class GroupRequest:
    GroupName: str = None
    SubAccount: str = None
    Department: str = None
    ViewEditBy: str = None
    AccessControl: str = None


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"GroupRequestDTO": GroupRequest})

__all__ = ["GroupRequest", "GroupRequestDTO"]
