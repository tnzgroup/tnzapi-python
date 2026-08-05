import base64

import pytest

from app.attachments import (
    MAX_ATTACHMENT_COUNT,
    MAX_ATTACHMENT_SIZE_BYTES,
    validate_attachment_count,
    validate_file_content,
)


def test_validate_file_content_accepts_small_valid_base64():
    assert validate_file_content("aGVsbG8=") == "aGVsbG8="


def test_validate_file_content_rejects_invalid_base64():
    with pytest.raises(ValueError, match="not valid base64"):
        validate_file_content("not valid base64!!")


def test_validate_file_content_rejects_oversized_payload_via_fast_encoded_length_precheck(monkeypatch):
    import app.attachments as attachments_module

    monkeypatch.setattr(attachments_module, "MAX_ATTACHMENT_SIZE_BYTES", 10)

    # b"short content" decodes to 13 bytes, itself already over the 10-byte limit - but that's
    # not what this test is isolating. The `match` below pins the assertion to the pre-check's
    # specific error message (not the decode-and-measure path's), proving the fast pre-check is
    # what actually fires here. A payload that decodes to <= 10 bytes could never make the
    # pre-check's own threshold (MAX*4//3+4) fire on its encoded length - the formula guarantees
    # that's mathematically impossible - so isolating the pre-check inherently means using
    # oversized-either-way input like this one; the real question this test answers is "does the
    # first check win," not "would the second check also have caught it."
    oversized_encoded = base64.b64encode(b"short content").decode()

    with pytest.raises(ValueError, match="encoded length implies more than"):
        attachments_module.validate_file_content(oversized_encoded)


def test_validate_file_content_rejects_content_that_decodes_over_the_limit(monkeypatch):
    import app.attachments as attachments_module

    monkeypatch.setattr(attachments_module, "MAX_ATTACHMENT_SIZE_BYTES", 5)

    # Encoded length alone doesn't exceed the fast pre-check bound for this input, so the real
    # decode-and-measure path is what must catch it.
    value = base64.b64encode(b"123456").decode()

    with pytest.raises(ValueError, match="decodes to"):
        attachments_module.validate_file_content(value)


def test_validate_attachment_count_accepts_none():
    assert validate_attachment_count(None) is None


def test_validate_attachment_count_accepts_up_to_the_limit():
    items = list(range(MAX_ATTACHMENT_COUNT))
    assert validate_attachment_count(items) == items


def test_validate_attachment_count_rejects_more_than_the_limit():
    items = list(range(MAX_ATTACHMENT_COUNT + 1))

    with pytest.raises(ValueError, match="exceeding the"):
        validate_attachment_count(items)
