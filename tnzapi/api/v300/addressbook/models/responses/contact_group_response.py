from dataclasses import dataclass, field


@dataclass
class ContactGroupResponse:
    Result: str = None
    ErrorMessage: list = field(default_factory=list)
    Contact: dict = None
    Group: dict = None


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"ContactGroupResponseDTO": ContactGroupResponse})

__all__ = ["ContactGroupResponse", "ContactGroupResponseDTO"]
