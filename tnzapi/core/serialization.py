class ToDictMixin:
    """Adds a real, round-trip-safe to_dict() to a dataclass, as the clean escape
    hatch dataclasses.asdict() can't provide once a field like `_extras` is
    attached as a plain (non-declared) instance attribute — see
    tnzapi/core/model_conversion.py's convert_list_field for why _extras is never a
    declared dataclass field. asdict(x) gives you the declared schema only;
    x.to_dict() gives you the declared schema plus any unrecognized API fields
    the SDK preserved for you.

    Recurses into nested ToDictMixin instances (and lists/dicts containing them)
    via their own to_dict(), so a full object graph serializes cleanly in one
    call. Does not filter None/empty values — that's filter_model_fields's job for
    outgoing *requests*; a response serializer must preserve shape.
    """

    def to_dict(self):
        result = {}
        for name in self.__class__.__dataclass_fields__:
            if name.startswith("_"):
                continue
            result[name] = _to_dict_value(getattr(self, name))

        extras = getattr(self, "_extras", None)
        if extras:
            for key, value in extras.items():
                result.setdefault(key, value)

        return result


def _to_dict_value(value):
    if isinstance(value, ToDictMixin):
        return value.to_dict()
    if isinstance(value, list):
        return [_to_dict_value(item) for item in value]
    if isinstance(value, dict):
        return {k: _to_dict_value(v) for k, v in value.items()}
    return value
