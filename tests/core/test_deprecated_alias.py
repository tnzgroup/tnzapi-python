import warnings

import pytest

from tnzapi.core.deprecated_alias import deprecated_alias


class _NewA:
    pass


class _NewB:
    pass


def test_returns_new_class_and_warns():
    getattr_fn = deprecated_alias({"OldA": _NewA})

    with pytest.warns(DeprecationWarning, match="OldA is deprecated, use _NewA instead"):
        result = getattr_fn("OldA")

    assert result is _NewA


def test_returns_the_same_object_not_a_copy():
    getattr_fn = deprecated_alias({"OldA": _NewA})

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        result = getattr_fn("OldA")

    assert result is _NewA


def test_raises_attribute_error_for_an_unmapped_name():
    getattr_fn = deprecated_alias({"OldA": _NewA})

    with pytest.raises(AttributeError):
        getattr_fn("SomethingElseEntirely")


def test_supports_multiple_aliases_in_one_mapping():
    getattr_fn = deprecated_alias({"OldA": _NewA, "OldB": _NewB})

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert getattr_fn("OldA") is _NewA
        assert getattr_fn("OldB") is _NewB


def test_a_real_dto_modules_all_includes_the_old_name_so_star_import_still_works():
    # __all__ must list BOTH the new and old names, or `from module import *`
    # (without __all__, Python only imports names already present in the
    # module's own __dict__, which the old name never is - it's synthesized
    # dynamically by __getattr__) would silently skip the old, deprecated name.
    import tnzapi.api.v300.messaging.models.responses.sms_response as module

    assert module.__all__ == ["SMSResponse", "SMSResponseDTO"]

    namespace = {}
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        exec("from tnzapi.api.v300.messaging.models.responses.sms_response import *", namespace)

    assert namespace["SMSResponseDTO"] is namespace["SMSResponse"]
