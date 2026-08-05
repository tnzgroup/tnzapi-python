from typing import ClassVar

from tnzapi.core.dict_compat import DictCompatMixin


def convert_list_field(value, target_cls):
    """Converts a raw list of dicts into a list of target_cls dataclass instances,
    for use inside a dataclass's __setattr__ override. Returns value unchanged if
    it isn't a list (e.g. None was assigned) - a non-list value must not crash here,
    matching the isinstance(value, list) guard convention already established in
    tnzapi/core/model_proxy.py. Idempotent: an item that's already a target_cls
    instance is left as-is, so re-assigning an already-converted list doesn't
    double-wrap it.

    Unlike parse_response()'s top-level "ignore unrecognized response fields"
    convention (which is safe because those fields are fully schema-captured),
    a formerly-untyped nested dict could have any key the real API returns, so an
    unknown key is not simply dropped here - if target_cls is a DictCompatMixin,
    unrecognized keys are preserved as a plain `_extras` instance attribute
    (attached after construction, deliberately NOT a declared dataclass field -
    dataclasses.asdict() can't be made to skip a declared field, so one would
    leak into serialization forever) and remain reachable via DictCompatMixin's
    dict-style access. If target_cls isn't a DictCompatMixin, unknown keys are
    dropped, matching the old behaviour.
    """
    if not isinstance(value, list):
        return value

    supports_extras = issubclass(target_cls, DictCompatMixin)

    converted = []
    for item in value:
        if isinstance(item, target_cls):
            converted.append(item)
        elif isinstance(item, dict):
            # Private-prefixed field names (e.g. a source dict with a key literally
            # named "_extras") are never treated as a "known" schema match - they
            # must still be routed into the extras bucket below, not passed as a
            # constructor kwarg (which would fail anyway now that _extras isn't a
            # declared field).
            public_fields = {
                name for name in target_cls.__dataclass_fields__ if not name.startswith("_")
            }
            filtered = {k: v for k, v in item.items() if k in public_fields}
            unknown = {k: v for k, v in item.items() if k not in public_fields}
            obj = target_cls(**filtered)
            if unknown and supports_extras:
                obj._extras = unknown
            converted.append(obj)
        else:
            converted.append(item)

    return converted


class TypedListFieldMixin:
    """Shared __setattr__ intercept so a dataclass field can hold typed instances
    of another dataclass instead of raw dicts, without every model hand-writing its
    own near-identical __setattr__ override calling convert_list_field(). A
    subclass declares which fields are typed via `_TYPED_LIST_FIELDS = {"FieldName":
    TargetModelClass}` (a plain, UNANNOTATED class attribute - see the warning below).

    Currently the only adopter of this mechanism is SMS (SMSStatus.Recipients,
    SMSRecipient.SMSReplies) - it's a pilot, not yet an established convention.
    Email/Fax/RCS/TTS/Voice/WhatsApp's own Recipients fields are deliberately still
    untyped `list` for now; rolling this out to them is a feature decision, not
    something this mixin's existence implies is already planned or in progress.

    IMPORTANT: the ClassVar annotation below belongs ONLY on this class. A `@dataclass`
    subclass must assign `_TYPED_LIST_FIELDS = {...}` with NO type annotation at all.
    `__dataclass_fields__` (which this codebase validates against everywhere -
    _is_public_field, _first_invalid_field, parse_response) retains ClassVar-annotated
    pseudo-fields; only dataclasses.fields() filters them out. Putting the ClassVar
    annotation on an actual @dataclass body would make `_TYPED_LIST_FIELDS` show up in
    that class's own __dataclass_fields__ - harmless only by coincidence (every relevant
    consumer already filters underscore-prefixed names), but a real landmine if this
    exact pattern is ever copied onto a *request* model, where ModelRequestMixin's
    _first_invalid_field does NOT filter underscores and would silently accept it as a
    valid Set() kwarg. @dataclass never scans a non-dataclass base's own annotations, so
    keeping the annotation here and assigning unannotated on the model itself sidesteps
    this entirely.
    """

    _TYPED_LIST_FIELDS: ClassVar[dict] = {}

    def __setattr__(self, name, value):
        target_cls = self._TYPED_LIST_FIELDS.get(name)
        if target_cls is not None:
            value = convert_list_field(value, target_cls)
        object.__setattr__(self, name, value)
