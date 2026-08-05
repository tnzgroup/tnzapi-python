import pytest

from tnzapi.core.destination import Destination, normalize_destination


def test_destination_accepts_known_fields():
    d = Destination(ToNumber="+64211111111", FirstName="Alice")

    assert d.ToNumber == "+64211111111"
    assert d.FirstName == "Alice"
    assert d.EmailAddress is None


def test_destination_rejects_unknown_field():
    with pytest.raises(TypeError):
        Destination(Bogus="x")


def test_destination_has_every_verified_field():
    expected = {
        "Recipient", "ToNumber", "MobilePhone", "MainPhone", "FaxNumber", "EmailAddress",
        "ContactID", "GroupID", "GroupCode", "Attention", "FirstName", "LastName", "Company",
        "Custom1", "Custom2", "Custom3", "Custom4", "Custom5", "Custom6", "Custom7", "Custom8", "Custom9",
    }
    assert set(Destination.__dataclass_fields__) == expected


def test_normalize_destination_with_string_wraps_in_primary_key():
    result = normalize_destination("+64211111111", primary_key="ToNumber")

    assert result == {"ToNumber": "+64211111111"}


def test_normalize_destination_with_string_uses_given_primary_key():
    result = normalize_destination("test@example.com", primary_key="EmailAddress")

    assert result == {"EmailAddress": "test@example.com"}


def test_normalize_destination_with_valid_dict_passes_through_unchanged():
    original = {"ToNumber": "+64211111111", "FirstName": "Alice"}

    result = normalize_destination(original, primary_key="ToNumber")

    assert result == original
    assert result is original


def test_normalize_destination_with_dict_rejects_unknown_key():
    with pytest.raises(ValueError, match="ToNunber"):
        normalize_destination({"ToNunber": "+64211111111"}, primary_key="ToNumber")


def test_normalize_destination_with_destination_instance_drops_unset_fields():
    result = normalize_destination(
        Destination(ToNumber="+64211111111", FirstName="Alice"), primary_key="ToNumber"
    )

    assert result == {"ToNumber": "+64211111111", "FirstName": "Alice"}


def test_normalize_destination_with_none_returns_none():
    assert normalize_destination(None, primary_key="ToNumber") is None


def test_normalize_destination_with_empty_destination_instance_returns_none():
    assert normalize_destination(Destination(), primary_key="ToNumber") is None
