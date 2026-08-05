from dataclasses import dataclass, field


@dataclass
class ReportError:
    Result: str = None
    ErrorMessage: list = field(default_factory=list)


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"ReportErrorDTO": ReportError})

__all__ = ["ReportError", "ReportErrorDTO"]
