import dataclasses

from app.responses import respond_with_result, validate_pagination


@dataclasses.dataclass
class _FakeResult:
    Result: str = None
    MessageID: str = None
    ErrorMessage: list = dataclasses.field(default_factory=list)


def test_respond_with_result_success_returns_200_with_full_body():
    result = _FakeResult(Result="Success", MessageID="msg-1")

    response = respond_with_result(result)

    assert response.status_code == 200
    assert response.body == b'{"Result":"Success","MessageID":"msg-1","ErrorMessage":[]}'


def test_respond_with_result_failure_returns_400_trimmed_body():
    result = _FakeResult(Result="Failed", MessageID="msg-1", ErrorMessage=["bad thing"])

    response = respond_with_result(result)

    assert response.status_code == 400
    assert response.body == b'{"Result":"Failed","ErrorMessage":["bad thing"]}'


@dataclasses.dataclass
class _FakeReplyWithExtras:
    MessageText: str = None
    _extras: dict = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class _FakeRecipientWithNestedReplies:
    Destination: str = None
    SMSReplies: list = dataclasses.field(default_factory=list)
    _extras: dict = dataclasses.field(default_factory=dict)


@dataclasses.dataclass
class _FakeStatusResultWithRecipients:
    Result: str = None
    Recipients: list = dataclasses.field(default_factory=list)
    ErrorMessage: list = dataclasses.field(default_factory=list)


def test_respond_with_result_strips_internal_extras_field_from_nested_dtos():
    reply = _FakeReplyWithExtras(MessageText="STOP", _extras={"Bogus": "x"})
    recipient = _FakeRecipientWithNestedReplies(
        Destination="+64211234567", SMSReplies=[reply], _extras={"Bogus": "y"}
    )
    result = _FakeStatusResultWithRecipients(Result="Success", Recipients=[recipient])

    response = respond_with_result(result)

    assert b"_extras" not in response.body
    assert b"Bogus" not in response.body
    assert b"STOP" in response.body
    assert b"+64211234567" in response.body


def test_validate_pagination_rejects_page_below_one():
    error = validate_pagination(page=0, records_per_page=20)

    assert error is not None
    assert error.status_code == 400


def test_validate_pagination_rejects_records_per_page_out_of_range():
    error = validate_pagination(page=1, records_per_page=0)
    assert error is not None
    assert error.status_code == 400

    error = validate_pagination(page=1, records_per_page=1001)
    assert error is not None
    assert error.status_code == 400


def test_validate_pagination_accepts_valid_values():
    error = validate_pagination(page=1, records_per_page=100)

    assert error is None
