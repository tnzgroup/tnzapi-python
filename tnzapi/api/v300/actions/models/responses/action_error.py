from dataclasses import dataclass, field


@dataclass
class ActionError:
    Result: str = None
    ErrorMessage: list = field(default_factory=list)


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"ActionErrorDTO": ActionError})

__all__ = ["ActionError", "ActionErrorDTO"]
