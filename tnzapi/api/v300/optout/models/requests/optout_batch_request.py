from dataclasses import dataclass, field


@dataclass
class OptOutBatchRequest:
    DestType: str = None
    Destination: str = None
    Destinations: list = field(default_factory=list)
    ContactID: str = None
    ContactIDs: list = field(default_factory=list)
    SubAccount: str = None
    Department: str = None


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"OptOutBatchRequestDTO": OptOutBatchRequest})

__all__ = ["OptOutBatchRequest", "OptOutBatchRequestDTO"]