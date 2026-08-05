from tnzapi.core.serialization import ToDictMixin


class DictCompatMixin(ToDictMixin):
    """Adds dict-style access (obj['Field'], obj.get('Field', default), 'Field' in obj,
    for k in obj, dict(obj), len(obj), obj.keys()/.items()/.values()) on top of normal
    attribute access, so a field that used to be a raw dict can be upgraded to a typed
    dataclass instance without breaking existing dict-based callers. Also inherits
    ToDictMixin's to_dict() for round-trip-safe serialization (see that class).

    Lookups only ever match declared, non-private dataclass fields (never mixin
    methods like `get` itself, and never a private-prefixed implementation field
    like `_extras` - that's the backing store, not a real key, and must not be
    handed out directly or a caller could mutate it through the leaked reference)
    plus, if `_extras` is present as a plain instance attribute (see
    tnzapi/core/model_conversion.py's convert_list_field), any key stored there -
    that's where an unrecognized API field gets stashed so it's preserved and
    still reachable rather than silently dropped.

    Iteration/length/keys() cover ALL declared public fields regardless of value
    (including ones that are None because the API didn't return them) plus any
    _extras keys - deliberately, not just the "populated" ones, to stay consistent
    with __contains__, which already returns True for a field the API never sent.
    Do not "fix" this to filter out None values later; that would make `in` and
    iteration disagree with each other.

    This intentionally does NOT subclass collections.abc.Mapping: doing so would
    silently flip isinstance(obj, Mapping) to True for every consumer (FastAPI/
    pydantic/json serializers commonly branch on exactly that check before their
    dataclass handling), which contradicts this mixin's whole purpose of not
    changing how existing callers see these objects.
    """

    def __getitem__(self, key):
        if _is_public_field(self, key):
            return getattr(self, key)
        extras = getattr(self, "_extras", None)
        if extras and key in extras:
            return extras[key]
        raise KeyError(key)

    def get(self, key, default=None):
        try:
            return self[key]
        except KeyError:
            return default

    def __contains__(self, key):
        if _is_public_field(self, key):
            return True
        extras = getattr(self, "_extras", None)
        return bool(extras and key in extras)

    def __iter__(self):
        yield from (name for name in self.__class__.__dataclass_fields__ if not name.startswith("_"))
        extras = getattr(self, "_extras", None)
        if extras:
            yield from extras.keys()

    def __len__(self):
        count = sum(1 for name in self.__class__.__dataclass_fields__ if not name.startswith("_"))
        extras = getattr(self, "_extras", None)
        return count + (len(extras) if extras else 0)

    def keys(self):
        return list(self)

    def items(self):
        return [(key, self[key]) for key in self]

    def values(self):
        return [self[key] for key in self]


def _is_public_field(obj, key):
    return isinstance(key, str) and not key.startswith("_") and key in obj.__class__.__dataclass_fields__
