import base64

import pytest

from tnzapi.core.file_attachment import (
    FileAttachment,
    read_file_as_base64,
    normalize_attachment,
    resolve_file_field,
)


def test_read_file_as_base64_round_trips(tmp_path):
    path = tmp_path / "greeting.wav"
    path.write_bytes(b"pretend-audio-bytes")

    encoded = read_file_as_base64(str(path))

    assert base64.b64decode(encoded) == b"pretend-audio-bytes"


def test_file_attachment_data_is_never_filesystem_checked(tmp_path):
    """Security regression test: a base64 string can coincidentally also be
    an existing local filename (e.g. "Makefile", "demo" - any all-letter
    string with length % 4 == 0 passes strict base64 validation). Data must
    be stored exactly as given, with no path check, under any circumstances."""
    real_file = tmp_path / "demo"
    real_file.write_bytes(b"this must never be read")

    attachment = FileAttachment(Name="evidence.txt", Data=str(real_file))

    assert attachment.Name == "evidence.txt"
    assert attachment.Data == str(real_file)


def test_file_attachment_with_literal_base64_data():
    attachment = FileAttachment(Name="test.pdf", Data="not-a-real-path-base64==")

    assert attachment.Name == "test.pdf"
    assert attachment.Data == "not-a-real-path-base64=="


def test_file_attachment_filename_reads_and_encodes_the_file(tmp_path):
    path = tmp_path / "greeting.wav"
    path.write_bytes(b"pretend-audio-bytes")

    attachment = FileAttachment(FileName=str(path))

    assert attachment.Name == "greeting.wav"
    assert base64.b64decode(attachment.Data) == b"pretend-audio-bytes"


def test_file_attachment_filename_positional_form(tmp_path):
    path = tmp_path / "greeting.wav"
    path.write_bytes(b"pretend-audio-bytes")

    attachment = FileAttachment(str(path))

    assert attachment.Name == "greeting.wav"
    assert base64.b64decode(attachment.Data) == b"pretend-audio-bytes"


def test_file_attachment_filename_keeps_explicit_name_override(tmp_path):
    path = tmp_path / "greeting.wav"
    path.write_bytes(b"pretend-audio-bytes")

    attachment = FileAttachment(str(path), Name="Custom.wav")

    assert attachment.Name == "Custom.wav"
    assert base64.b64decode(attachment.Data) == b"pretend-audio-bytes"


def test_file_attachment_filename_and_data_together_raises(tmp_path):
    path = tmp_path / "greeting.wav"
    path.write_bytes(b"pretend-audio-bytes")

    with pytest.raises(ValueError, match="pass either FileName or Data, not both"):
        FileAttachment(FileName=str(path), Data="already-base64==")


def test_file_attachment_filename_that_does_not_exist_raises(tmp_path):
    with pytest.raises(FileNotFoundError):
        FileAttachment(FileName=str(tmp_path / "does-not-exist.wav"))


def test_normalize_attachment_returns_none_for_none():
    assert normalize_attachment(None) is None


def test_normalize_attachment_accepts_file_attachment_instance():
    attachment = FileAttachment(Name="test.pdf", Data="base64data==")

    assert normalize_attachment(attachment) == {"Name": "test.pdf", "Data": "base64data=="}


def test_normalize_attachment_accepts_valid_dict():
    result = normalize_attachment({"Name": "test.pdf", "Data": "base64data=="})

    assert result == {"Name": "test.pdf", "Data": "base64data=="}


def test_normalize_attachment_rejects_unknown_dict_key():
    with pytest.raises(ValueError, match="Unknown attachment field: Bogus"):
        normalize_attachment({"Name": "test.pdf", "Bogus": "x"})


def test_normalize_attachment_rejects_filename_as_a_dict_key():
    """FileName is a constructor-only convenience, never a valid dict key -
    a dict is always the literal wire shape (Name/Data only), so its Data can
    never be silently reinterpreted as a path."""
    with pytest.raises(ValueError, match="Unknown attachment field: FileName"):
        normalize_attachment({"Name": "test.pdf", "FileName": "/some/path"})


def test_normalize_attachment_dict_data_is_never_filesystem_checked(tmp_path):
    real_file = tmp_path / "demo"
    real_file.write_bytes(b"this must never be read")

    result = normalize_attachment({"Name": "evidence.txt", "Data": str(real_file)})

    assert result == {"Name": "evidence.txt", "Data": str(real_file)}


def test_normalize_attachment_bare_real_path_string_resolves_name_and_data(tmp_path):
    path = tmp_path / "Invoice.pdf"
    path.write_bytes(b"pdf-bytes")

    result = normalize_attachment(str(path))

    assert result["Name"] == "Invoice.pdf"
    assert base64.b64decode(result["Data"]) == b"pdf-bytes"


def test_normalize_attachment_bare_non_path_string_raises():
    with pytest.raises(ValueError, match="is not an existing file path"):
        normalize_attachment("definitely-not-a-real-file.pdf")


def test_resolve_file_field_unwraps_file_attachment():
    attachment = FileAttachment(Name="greeting.wav", Data="already-resolved-base64==")

    result = resolve_file_field(attachment)

    assert result == "already-resolved-base64=="


def test_resolve_file_field_resolves_a_real_path_string(tmp_path):
    path = tmp_path / "greeting.wav"
    path.write_bytes(b"audio-bytes")

    result = resolve_file_field(str(path))

    assert base64.b64decode(result) == b"audio-bytes"


def test_resolve_file_field_passes_a_non_path_string_through_unchanged():
    assert resolve_file_field("literal-base64-audio==") == "literal-base64-audio=="


def test_resolve_file_field_passes_none_through_unchanged():
    assert resolve_file_field(None) is None