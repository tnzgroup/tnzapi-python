from dataclasses import dataclass, field


@dataclass
class TTSActionResult:
    Result: str = None
    ActionResult: str = None
    MessageID: str = None
    JobNum: str = None
    Status: str = None
    Action: str = None
    ErrorMessage: list = field(default_factory=list)


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"TTSActionResultDTO": TTSActionResult})

__all__ = ["TTSActionResult", "TTSActionResultDTO"]