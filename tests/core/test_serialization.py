from dataclasses import dataclass, field
from typing import Optional

from tnzapi.core.dict_compat import DictCompatMixin
from tnzapi.core.serialization import ToDictMixin


@dataclass
class FakeLeafDTO(DictCompatMixin):
    Name: Optional[str] = None


@dataclass
class FakeParentDTO(ToDictMixin):
    Result: Optional[str] = None
    Children: list = field(default_factory=list)


def test_to_dict_returns_public_fields_only():
    obj = FakeLeafDTO(Name="Alice")

    assert obj.to_dict() == {"Name": "Alice"}


def test_to_dict_merges_extras_at_the_same_level():
    obj = FakeLeafDTO(Name="Alice")
    obj._extras = {"Bogus": "x"}

    assert obj.to_dict() == {"Name": "Alice", "Bogus": "x"}


def test_to_dict_never_lets_extras_clobber_a_declared_field():
    obj = FakeLeafDTO(Name="Alice")
    obj._extras = {"Name": "should-not-win"}

    assert obj.to_dict() == {"Name": "Alice"}


def test_to_dict_recurses_into_nested_to_dict_mixin_lists():
    parent = FakeParentDTO(Result="Success", Children=[FakeLeafDTO(Name="Alice")])

    assert parent.to_dict() == {"Result": "Success", "Children": [{"Name": "Alice"}]}


def test_to_dict_recurses_into_nested_extras_too():
    child = FakeLeafDTO(Name="Alice")
    child._extras = {"Bogus": "x"}
    parent = FakeParentDTO(Result="Success", Children=[child])

    assert parent.to_dict() == {"Result": "Success", "Children": [{"Name": "Alice", "Bogus": "x"}]}


def test_to_dict_does_not_filter_none_values():
    obj = FakeLeafDTO()

    assert obj.to_dict() == {"Name": None}
