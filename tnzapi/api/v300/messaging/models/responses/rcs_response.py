from dataclasses import dataclass, field


@dataclass
class RCSResponse:
    Result: str = None
    MessageID: str = None
    ErrorMessage: list = field(default_factory=list)


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"RCSResponseDTO": RCSResponse})

__all__ = ["RCSResponse", "RCSResponseDTO"]
