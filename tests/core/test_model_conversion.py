from dataclasses import dataclass
from typing import Optional

from tnzapi.core.dict_compat import DictCompatMixin
from tnzapi.core.model_conversion import convert_list_field


@dataclass
class FakeItemDTO:
    Name: Optional[str] = None
    Age: Optional[int] = None


@dataclass
class FakeItemWithExtrasDTO(DictCompatMixin):
    # _extras is deliberately NOT declared as a field here - convert_list_field
    # now decides "does this target support extras?" via issubclass(DictCompatMixin),
    # not by checking for a declared _extras field (dataclasses.asdict() can't skip
    # a declared field, so _extras must be a plain post-construction attribute -
    # see tnzapi/core/model_conversion.py's docstring for the full reasoning).
    Name: Optional[str] = None


def test_converts_list_of_dicts_to_target_class_instances():
    result = convert_list_field([{"Name": "Alice", "Age": 30}], FakeItemDTO)

    assert len(result) == 1
    assert isinstance(result[0], FakeItemDTO)
    assert result[0].Name == "Alice"
    assert result[0].Age == 30


def test_drops_unknown_keys_when_converting():
    result = convert_list_field([{"Name": "Alice", "Bogus": "x"}], FakeItemDTO)

    assert result[0].Name == "Alice"
    assert not hasattr(result[0], "Bogus")


def test_preserves_unknown_keys_in_extras_when_target_supports_it():
    result = convert_list_field([{"Name": "Alice", "Bogus": "x"}], FakeItemWithExtrasDTO)

    assert result[0].Name == "Alice"
    assert result[0]._extras == {"Bogus": "x"}


def test_a_source_key_literally_named_extras_is_preserved_not_overwritten():
    result = convert_list_field(
        [{"Name": "Alice", "_extras": "user-value-that-should-survive"}],
        FakeItemWithExtrasDTO,
    )

    assert result[0]._extras == {"_extras": "user-value-that-should-survive"}


def test_leaves_already_converted_instances_unchanged():
    original = FakeItemDTO(Name="Alice")

    result = convert_list_field([original], FakeItemDTO)

    assert result[0] is original


def test_non_list_value_passes_through_unchanged():
    assert convert_list_field(None, FakeItemDTO) is None
    assert convert_list_field("not a list", FakeItemDTO) == "not a list"


def test_empty_list_stays_empty():
    assert convert_list_field([], FakeItemDTO) == []


def test_typed_list_fields_does_not_pollute_dataclass_fields():
    from tnzapi.api.v300.messaging.models.responses.sms_recipient import SMSRecipient
    from tnzapi.api.v300.messaging.models.responses.sms_status import SMSStatus

    assert "_TYPED_LIST_FIELDS" not in SMSStatus.__dataclass_fields__
    assert "_TYPED_LIST_FIELDS" not in SMSRecipient.__dataclass_fields__


def test_typed_list_field_mixin_converts_declared_field_and_leaves_others_alone():
    from tnzapi.core.model_conversion import TypedListFieldMixin

    class FakeParent(TypedListFieldMixin):
        _TYPED_LIST_FIELDS = {"Items": FakeItemDTO}

        def __init__(self):
            self.Items = [{"Name": "Alice"}]
            self.Other = [{"Name": "Bob"}]

    parent = FakeParent()

    assert isinstance(parent.Items[0], FakeItemDTO)
    assert parent.Other == [{"Name": "Bob"}]


def test_typed_list_field_mixin_passes_through_non_list_value():
    from tnzapi.core.model_conversion import TypedListFieldMixin

    class FakeParent(TypedListFieldMixin):
        _TYPED_LIST_FIELDS = {"Items": FakeItemDTO}

        def __init__(self):
            self.Items = None

    assert FakeParent().Items is None
