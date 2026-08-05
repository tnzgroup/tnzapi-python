from dataclasses import dataclass


@dataclass
class OptOutRequest:
    DestType: str = None
    Destination: str = None
    ContactID: str = None
    SubAccount: str = None
    Department: str = None
    StopMessage: str = None
    Notes: str = None


from tnzapi.core.deprecated_alias import deprecated_alias

__getattr__ = deprecated_alias({"OptOutRequestDTO": OptOutRequest})

__all__ = ["OptOutRequest", "OptOutRequestDTO"]