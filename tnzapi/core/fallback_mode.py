"""normalize_fallback_mode - joins a FallbackMode list into TNZ's real wire
format (a comma-separated string, e.g. "Voice, WAPP"), matching the
confirmed-against-the-live-API behavior in tnzapi-dotnet's EnumListHelper.

A plain FallbackMode="SMS" string call site is left completely untouched -
this is purely additive over the SDK's existing single-string support.
"""


def normalize_fallback_mode(value):
    if value is None:
        return None
    if isinstance(value, (list, tuple)):
        return ", ".join(_to_wire_token(v) for v in value)
    if isinstance(value, str):
        return _to_wire_token(value)
    return value


def _to_wire_token(mode: str) -> str:
    # Confirmed against the live API (see tnzapi-dotnet's EnumListHelper):
    # every FallbackMode value's wire token matches its name exactly,
    # except WhatsApp, whose wire token is "WAPP".
    return "WAPP" if mode == "WhatsApp" else mode
