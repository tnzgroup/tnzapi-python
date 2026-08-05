from dataclasses import dataclass, field


@dataclass
class GroupContactResponse:
    Result: str = None
    ErrorMessage: list = field(default_factory=list)
    Group: dict = None
    Contact: dict = None


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"GroupContactResponseDTO": GroupContactResponse})

__all__ = ["GroupContactResponse", "GroupContactResponseDTO"]
