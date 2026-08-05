import warnings

import pytest

from tnzapi.core.legacy_kwargs import accept_legacy_kwargs


@accept_legacy_kwargs({"message_id": "MessageID", "records_per_page": "RecordsPerPage"})
def _sample(MessageID, RecordsPerPage=20):
    return {"MessageID": MessageID, "RecordsPerPage": RecordsPerPage}


def test_new_name_works_directly():
    assert _sample(MessageID="msg-1", RecordsPerPage=50) == {"MessageID": "msg-1", "RecordsPerPage": 50}


def test_positional_call_is_unaffected():
    assert _sample("msg-1") == {"MessageID": "msg-1", "RecordsPerPage": 20}


def test_old_snake_case_name_still_works_with_warning():
    with pytest.warns(DeprecationWarning, match="message_id.*MessageID"):
        result = _sample(message_id="msg-1")
    assert result == {"MessageID": "msg-1", "RecordsPerPage": 20}


def test_old_and_new_name_together_raises_type_error():
    with pytest.raises(TypeError, match="MessageID.*message_id"):
        _sample(MessageID="msg-1", message_id="msg-2")


def test_required_new_name_missing_entirely_still_raises_type_error():
    with pytest.raises(TypeError):
        _sample()


def test_multiple_old_names_in_one_call_all_translate():
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        result = _sample(message_id="msg-1", records_per_page=99)
    assert result == {"MessageID": "msg-1", "RecordsPerPage": 99}
