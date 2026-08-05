from dataclasses import dataclass, field
from typing import Optional

import pytest

from tnzapi.core.dict_compat import DictCompatMixin


@dataclass
class FakeDTO(DictCompatMixin):
    Name: Optional[str] = None
    Age: Optional[int] = None


@dataclass
class FakeDTOWithExtras(DictCompatMixin):
    Name: Optional[str] = None
    _extras: dict = field(default_factory=dict)


def test_getitem_returns_field_value():
    obj = FakeDTO(Name="Alice", Age=30)

    assert obj["Name"] == "Alice"
    assert obj["Age"] == 30


def test_getitem_raises_key_error_for_unknown_field():
    obj = FakeDTO(Name="Alice")

    with pytest.raises(KeyError):
        obj["Bogus"]


def test_get_returns_field_value():
    obj = FakeDTO(Name="Alice")

    assert obj.get("Name") == "Alice"


def test_get_returns_default_for_unknown_field():
    obj = FakeDTO(Name="Alice")

    assert obj.get("Bogus") is None
    assert obj.get("Bogus", "fallback") == "fallback"


def test_contains_reflects_known_fields():
    obj = FakeDTO(Name="Alice")

    assert "Name" in obj
    assert "Bogus" not in obj


def test_attribute_access_still_works_alongside_dict_access():
    obj = FakeDTO(Name="Alice", Age=30)

    assert obj.Name == "Alice"
    assert obj["Name"] == obj.Name


def test_getitem_does_not_expose_mixin_methods_as_keys():
    obj = FakeDTO(Name="Alice")

    with pytest.raises(KeyError):
        obj["get"]


def test_get_does_not_expose_mixin_methods_as_keys():
    obj = FakeDTO(Name="Alice")

    assert obj.get("get") is None


def test_contains_does_not_expose_mixin_methods_as_keys():
    obj = FakeDTO(Name="Alice")

    assert "get" not in obj


def test_getitem_does_not_expose_the_extras_backing_field_itself():
    obj = FakeDTOWithExtras(Name="Alice")

    with pytest.raises(KeyError):
        obj["_extras"]


def test_get_does_not_expose_the_extras_backing_field_itself():
    obj = FakeDTOWithExtras(Name="Alice")

    assert obj.get("_extras") is None


def test_contains_does_not_expose_the_extras_backing_field_itself():
    obj = FakeDTOWithExtras(Name="Alice")

    assert "_extras" not in obj


def test_keys_actually_stored_in_extras_remain_reachable():
    obj = FakeDTOWithExtras(Name="Alice", _extras={"Bogus": "x"})

    assert obj["Bogus"] == "x"
    assert obj.get("Bogus") == "x"
    assert "Bogus" in obj


def test_iterating_yields_public_field_names_including_none_valued_ones():
    obj = FakeDTO(Name="Alice")

    assert list(obj) == ["Name", "Age"]


def test_iterating_includes_extras_keys_after_public_fields():
    obj = FakeDTOWithExtras(Name="Alice", _extras={"Bogus": "x"})

    assert list(obj) == ["Name", "Bogus"]


def test_dict_constructor_round_trips_correctly():
    obj = FakeDTO(Name="Alice", Age=30)

    assert dict(obj) == {"Name": "Alice", "Age": 30}


def test_dict_constructor_includes_extras():
    obj = FakeDTOWithExtras(Name="Alice", _extras={"Bogus": "x"})

    assert dict(obj) == {"Name": "Alice", "Bogus": "x"}


def test_len_counts_public_fields_plus_extras():
    obj = FakeDTO(Name="Alice", Age=30)
    assert len(obj) == 2

    obj_with_extras = FakeDTOWithExtras(Name="Alice", _extras={"Bogus": "x", "Other": "y"})
    assert len(obj_with_extras) == 3


def test_keys_items_values_agree_with_manual_iteration():
    obj = FakeDTOWithExtras(Name="Alice", _extras={"Bogus": "x"})

    assert obj.keys() == list(obj)
    assert obj.items() == [(k, obj[k]) for k in obj]
    assert obj.values() == [obj[k] for k in obj]


def test_non_string_key_getitem_raises_key_error_not_attribute_error():
    obj = FakeDTO(Name="Alice")

    with pytest.raises(KeyError):
        obj[0]


def test_non_string_key_get_returns_default_not_crash():
    obj = FakeDTO(Name="Alice")

    assert obj.get(0) is None


def test_non_string_key_contains_returns_false_not_crash():
    obj = FakeDTO(Name="Alice")

    assert (0 in obj) is False


def test_for_loop_iteration_does_not_crash():
    obj = FakeDTO(Name="Alice", Age=30)

    collected = [key for key in obj]

    assert collected == ["Name", "Age"]
