import dataclasses

from fastapi.responses import JSONResponse


def _strip_internal_keys(value):
    """dataclasses.asdict() recurses into every nested dataclass field. tnzapi's
    typed DTOs (e.g. SMSRecipient/SMSReply) keep any SDK-internal overflow
    state (like an unrecognized-field store) as a plain instance attribute rather
    than a declared dataclass field specifically so asdict() can't see it - so
    this strip is generic defense-in-depth against a future internal SDK field
    that *is* declared, not a fix for a currently-real leak.
    """
    if isinstance(value, dict):
        return {k: _strip_internal_keys(v) for k, v in value.items() if not k.startswith("_")}
    if isinstance(value, list):
        return [_strip_internal_keys(item) for item in value]
    return value


def respond_with_result(result) -> JSONResponse:
    body = _strip_internal_keys(dataclasses.asdict(result))

    if body.get("Result") == "Success":
        return JSONResponse(status_code=200, content=body)

    return JSONResponse(
        status_code=400,
        content={"Result": body.get("Result"), "ErrorMessage": body.get("ErrorMessage", [])},
    )


def validate_pagination(page: int, records_per_page: int, max_records_per_page: int = 1000):
    if page < 1:
        return JSONResponse(
            status_code=400,
            content={"Result": "Failed", "ErrorMessage": [f"Invalid page: '{page}' must be at least 1."]},
        )

    if records_per_page < 1 or records_per_page > max_records_per_page:
        return JSONResponse(
            status_code=400,
            content={
                "Result": "Failed",
                "ErrorMessage": [
                    f"Invalid recordsPerPage: '{records_per_page}' must be between 1 and {max_records_per_page}."
                ],
            },
        )

    return None
