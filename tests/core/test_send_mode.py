import json
from dataclasses import dataclass, asdict

from tnzapi.core.send_mode import SendMode


def test_send_mode_test_equals_plain_string():
    assert SendMode.Test == "Test"


def test_send_mode_live_equals_plain_string():
    assert SendMode.Live == "Live"


def test_send_mode_members_are_str_instances():
    assert isinstance(SendMode.Test, str)
    assert isinstance(SendMode.Live, str)


def test_send_mode_serializes_as_plain_string_via_asdict_and_json():
    @dataclass
    class _FakeRequest:
        Mode: str = None

    body = asdict(_FakeRequest(Mode=SendMode.Test))
    assert json.loads(json.dumps(body)) == {"Mode": "Test"}


def test_send_mode_not_stripped_by_filter_model_fields():
    from tnzapi.core.model_proxy import filter_model_fields

    @dataclass
    class _FakeRequest:
        Mode: str = None

    filtered = filter_model_fields(_FakeRequest(Mode=SendMode.Test))
    assert filtered == {"Mode": "Test"}
