import copy
import inspect
import os
from dataclasses import asdict

from tnzapi.core.destination import Destination, normalize_destination
from tnzapi.core.fallback_mode import normalize_fallback_mode
from tnzapi.core.file_attachment import (
    FileAttachment,
    _FILE_ATTACHMENT_FIELD_NAMES,
    normalize_attachment,
    resolve_file_field,
)


def filter_model_fields(obj) -> dict:
    return {k: v for k, v in asdict(obj).items() if v not in (None, [], "")}


def project_model(source, target_cls):
    """Builds a target_cls instance from source's fields, keeping only the
    fields target_cls actually declares - lets Create()/Update() accept a
    Response instance as model= without its read-only fields (ContactID,
    Owner, timestamps, Result, ErrorMessage, Groups, ...) leaking into the
    outgoing request body.
    """
    known = target_cls.__dataclass_fields__
    values = {k: v for k, v in asdict(source).items() if k in known}
    return target_cls(**values)


def require_id(value, id_field):
    """Raises ValueError if value - a plain, required ID parameter with no
    Response-instance duality (e.g. MessageID/ContactID/GroupID passed
    directly to Status()/Detail()/Delete()/List()/etc.) - is None or "".
    Otherwise the caller would silently end up building a URL like
    ".../contact/None" (or, for an ID compared in-memory rather than sent
    over the wire, silently never matching anything) from an unset ID.
    Returns value unchanged otherwise, so it composes into an assignment:
    ContactID = require_id(ContactID, "ContactID").
    """
    if value is None or value == "":
        raise ValueError(f"{id_field} is required")
    return value


def resolve_id(value, response_cls, id_field):
    """Lets an ID parameter (Update()/Delete()) accept either a plain ID
    string or the Response instance it came from (e.g. from Detail()),
    extracting id_field in the latter case - so a caller can pass back
    exactly what a prior call returned instead of pulling the id out
    themselves.

    Raises ValueError if the resolved ID is unset - either because it was
    extracted from a Response whose id_field is unset (e.g. a failed or
    partially-populated Response), or because the caller passed None/""
    directly as value (delegated to require_id) - otherwise either path
    would silently end up building a URL like ".../contact/None".
    """
    if isinstance(value, response_cls):
        value = getattr(value, id_field)
        if value is None or value == "":
            raise ValueError(
                f"Cannot resolve an ID from this {response_cls.__name__} - "
                f"its {id_field} field is not set"
            )
        return value

    return require_id(value, id_field)


class ModelRequestMixin:
    """Shared _data-proxying builder mechanics for every v300 request class
    that exposes Set()/Build() over a settable request-body model (messaging
    channels, Contact, Group, OptOut).

    Concrete classes must:
    - set a class attribute `_request_model_cls` pointing at their own
      @dataclass request model
    - call `self._reset()` at the end of `__init__`, after `self.user`/
      `self.http` are set

    This mixin owns no state itself beyond what `_reset()` establishes on
    the instance (`self._data`), so it needs no `__init__` of its own.

    A subclass that stores extra instance state beyond `user`/`http`/`_data`
    must extend `_INSTANCE_ATTRS` accordingly, e.g.:
        _INSTANCE_ATTRS = ModelRequestMixin._INSTANCE_ATTRS | {"_retry_count"}
    otherwise a same-named model field would silently steal that assignment.
    """

    _INSTANCE_ATTRS = frozenset({"user", "http", "_data"})

    # The field a bare string shorthand in a Destinations list maps to (e.g.
    # Set(Destinations=["+64211234567"])). Every messaging channel overrides this
    # to match its own AddDestination()'s primary_key - "EmailAddress" on Email,
    # "ToNumber" (this default) on the other 7 - so Set()/SendMessage() and
    # AddDestination() can never disagree on how the same bare string is handled.
    _destination_primary_key = "ToNumber"

    # Field names on this class's own request DTO whose values should be
    # resolved via resolve_file_field() (file path / legacy base64 str /
    # FileAttachment -> plain base64 str) inside _apply_fields, rather than
    # being set verbatim. Empty by default - only Voice overrides this today.
    _FILE_OR_PATH_FIELDS = frozenset()

    # Field names on this class's own request DTO whose values should be
    # resolved via normalize_fallback_mode() (list/tuple of mode names ->
    # comma-joined wire string, with "WhatsApp" translated to the real wire
    # token "WAPP") inside _apply_fields, rather than being set verbatim.
    # Empty by default - only SMS/RCS/WhatsApp override this today.
    _FALLBACK_MODE_FIELDS = frozenset()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if not inspect.isabstract(cls) and not hasattr(cls, "_request_model_cls"):
            raise TypeError(f"{cls.__name__} must define '_request_model_cls'")

    def _reset(self):
        self._data = self._request_model_cls()

    def __setattr__(self, name, value):
        if name in self._INSTANCE_ATTRS or not hasattr(self, "_data") or name not in type(self._data).__dataclass_fields__:
            super().__setattr__(name, value)
        else:
            setattr(self._data, name, value)

    def __getattr__(self, name):
        if "_data" not in self.__dict__:
            raise AttributeError(name)
        return getattr(self._data, name)

    def _build_request_body(self) -> dict:
        return filter_model_fields(self._data)

    def _first_invalid_field(self, fields: dict):
        for key in fields:
            if key not in type(self._data).__dataclass_fields__:
                return key
        if "Destinations" in fields and isinstance(fields["Destinations"], list):
            for item in fields["Destinations"]:
                if isinstance(item, dict):
                    invalid = next((k for k in item if k not in Destination.__dataclass_fields__), None)
                    if invalid:
                        return invalid
                elif item is not None and not isinstance(item, (str, Destination)):
                    # Anything else (int, list, ...) would otherwise pass through
                    # normalize_destination() as-is and get silently dropped in
                    # _apply_fields (it only recognizes dict/Destination/str/None) -
                    # rejecting it here turns that into the SDK's normal
                    # ValueError (Set())/Result="Failed" (SendMessage()) contract
                    # instead of a silent, hard-to-notice empty Destinations list.
                    return f"Destinations item of type {type(item).__name__}"
        if "Files" in fields and isinstance(fields["Files"], list):
            for item in fields["Files"]:
                if isinstance(item, dict):
                    invalid = next((k for k in item if k not in _FILE_ATTACHMENT_FIELD_NAMES), None)
                    if invalid:
                        return invalid
                elif isinstance(item, str):
                    if not item or not os.path.isfile(item):
                        return f"Files item (not an existing file path): {item!r}"
                elif item is not None and not isinstance(item, FileAttachment):
                    return f"Files item of type {type(item).__name__}"
        return None

    def _apply_fields(self, fields: dict):
        for key, value in fields.items():
            if key == "Destinations" and isinstance(value, list):
                # SendMessage(model=<Request model instance>) bypasses this entirely
                # (it deep-copies the model wholesale, never calling _apply_fields) -
                # a hand-built model with raw strings in Destinations still goes
                # unnormalized. Known, pre-existing asymmetry, not fixed here.
                value = [
                    normalize_destination(item, primary_key=self._destination_primary_key)
                    for item in value
                ]
                value = [item for item in value if item is not None]
            elif key == "Files" and isinstance(value, list):
                value = [normalize_attachment(item) for item in value]
                value = [item for item in value if item is not None]
            elif key in type(self)._FILE_OR_PATH_FIELDS:
                value = resolve_file_field(value)
            elif key in type(self)._FALLBACK_MODE_FIELDS:
                value = normalize_fallback_mode(value)
            setattr(self, key, value)

    def _missing_destination_error(self, response_cls):
        """Returns a Result="Failed" response_cls instance if self._data has no
        destination set via any of the documented alternatives - Destinations,
        Destination, the channel's own primary field (self._destination_primary_key -
        "ToNumber" for most channels, "EmailAddress" for Email), or ContactID/GroupID
        (every channel's own docs list these as valid standalone alternatives, e.g.
        docs/sms.md's Parameters table) - or None if a destination is present.

        A single shared check, not duplicated per channel, specifically so a fix to
        what counts as a valid destination (e.g. this method itself, when the
        ContactID/GroupID gap was found) only has to be made once.
        """
        primary_field = self._destination_primary_key
        if (
            self._data.Destinations
            or self._data.Destination
            or getattr(self._data, primary_field)
            or self._data.ContactID
            or self._data.GroupID
        ):
            return None

        return response_cls(
            Result="Failed",
            ErrorMessage=[f"Missing required field: Destinations, Destination, ContactID, GroupID, or {primary_field}"],
        )

    def Set(self, **kwargs):

        invalid = self._first_invalid_field(kwargs)
        if invalid:
            raise ValueError(f"Unknown argument: {invalid}")

        self._apply_fields(kwargs)
        return self

    def Build(self):
        return copy.deepcopy(self._data)