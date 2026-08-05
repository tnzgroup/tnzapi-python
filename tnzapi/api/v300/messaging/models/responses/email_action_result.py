from dataclasses import dataclass, field


@dataclass
class EmailActionResult:
    Result: str = None
    ActionResult: str = None
    MessageID: str = None
    JobNum: str = None
    Status: str = None
    Action: str = None
    ErrorMessage: list = field(default_factory=list)


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"EmailActionResultDTO": EmailActionResult})

__all__ = ["EmailActionResult", "EmailActionResultDTO"]