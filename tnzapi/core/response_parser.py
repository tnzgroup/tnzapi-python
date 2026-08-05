import json


def _parse_json_or_default(text: str, default):

    if not text:
        return default

    try:
        return json.loads(text)
    except ValueError:
        return default


def _extract_error_messages(parsed_body: dict) -> list:

    raw = parsed_body.get("ErrorMessage") if isinstance(parsed_body, dict) else None

    if raw is None:
        return []

    if isinstance(raw, list):
        return [str(item) for item in raw if item]

    return [str(raw)]


def _map_status_to_result(status_code: int) -> str:

    if status_code == 401:
        return "Unauthorized"

    if status_code == 404:
        return "RecordNotFound"

    return "Failed"


def parse_response(response, result_cls, error_cls=None):

    if 200 <= response.status_code < 300:

        if not response.text:
            return result_cls(Result="Failed", ErrorMessage=[
                "Received a successful HTTP status but the response body was empty."
            ])

        parsed = _parse_json_or_default(response.text, None)
        if parsed is None:
            return result_cls(Result="Failed", ErrorMessage=[
                f"Received a successful HTTP status but the response body could not be parsed."
            ])

        result = result_cls()
        for key, value in parsed.items():
            if key in type(result).__dataclass_fields__:
                setattr(result, key, value)

        if not result.Result:
            result.Result = "Success"

        return result

    parsed = _parse_json_or_default(response.text, {})

    return result_cls(
        Result=_map_status_to_result(response.status_code),
        ErrorMessage=_extract_error_messages(parsed),
    )