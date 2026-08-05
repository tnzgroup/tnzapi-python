from dataclasses import dataclass, field
import requests
from tnzapi.core.response_parser import parse_response


@dataclass
class FakeResultDTO:
    Result: str = None
    MessageID: str = None
    ErrorMessage: list = field(default_factory=list)


def _fake_response(status_code, body_text):
    r = requests.Response()
    r.status_code = status_code
    r._content = body_text.encode("utf-8")
    return r


def test_200_with_no_result_field_is_still_success():
    # Real backend behavior: on genuine success, the "Result" field is omitted entirely.
    r = _fake_response(200, '{"MessageID": "abc123"}')
    result = parse_response(r, FakeResultDTO)
    assert result.Result == "Success"
    assert result.MessageID == "abc123"


def test_200_with_empty_body_is_a_failure():
    r = _fake_response(200, "")
    result = parse_response(r, FakeResultDTO)
    assert result.Result == "Failed"
    assert "empty" in result.ErrorMessage[0].lower()


def test_401_maps_to_unauthorized():
    r = _fake_response(401, '{"ErrorMessage": ["Access denied"]}')
    result = parse_response(r, FakeResultDTO)
    assert result.Result == "Unauthorized"
    assert result.ErrorMessage == ["Access denied"]


def test_404_maps_to_record_not_found():
    r = _fake_response(404, '{"ErrorMessage": ["Not found"]}')
    result = parse_response(r, FakeResultDTO)
    assert result.Result == "RecordNotFound"


def test_400_maps_to_failed_and_accepts_scalar_error_message():
    # OpenAPI spec examples are inconsistent: sometimes ErrorMessage is a bare string, not an array.
    r = _fake_response(400, '{"ErrorMessage": "Missing or empty field"}')
    result = parse_response(r, FakeResultDTO)
    assert result.Result == "Failed"
    assert result.ErrorMessage == ["Missing or empty field"]


def test_dunder_key_in_response_body_does_not_corrupt_the_result():
    # A response body containing a key like "__dict__" must not be applied via
    # setattr - that would silently replace the whole instance dict (a real,
    # confirmed bug when field selection used hasattr() instead of checking
    # __dataclass_fields__, since every object has a __dict__ attribute).
    r = _fake_response(200, '{"MessageID": "abc123", "__dict__": {"corrupted": true}}')
    result = parse_response(r, FakeResultDTO)
    assert result.MessageID == "abc123"
    assert result.Result == "Success"
