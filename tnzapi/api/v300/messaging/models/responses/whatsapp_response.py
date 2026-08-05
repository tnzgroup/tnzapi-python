from dataclasses import dataclass, field


@dataclass
class WhatsAppResponse:
    Result: str = None
    MessageID: str = None
    ErrorMessage: list = field(default_factory=list)


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"WhatsAppResponseDTO": WhatsAppResponse})

__all__ = ["WhatsAppResponse", "WhatsAppResponseDTO"]
