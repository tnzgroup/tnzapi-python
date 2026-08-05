from dataclasses import dataclass, field


@dataclass
class FaxResponse:
    Result: str = None
    MessageID: str = None
    ErrorMessage: list = field(default_factory=list)


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"FaxResponseDTO": FaxResponse})

__all__ = ["FaxResponse", "FaxResponseDTO"]