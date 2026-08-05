from dataclasses import dataclass, field


@dataclass
class VoiceResponse:
    Result: str = None
    MessageID: str = None
    ErrorMessage: list = field(default_factory=list)


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"VoiceResponseDTO": VoiceResponse})

__all__ = ["VoiceResponse", "VoiceResponseDTO"]