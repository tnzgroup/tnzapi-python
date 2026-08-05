import base64
import os
from dataclasses import InitVar, asdict, dataclass, fields
from typing import Optional


def read_file_as_base64(path: str) -> str:
    """Reads a local file and returns its contents as a base64-encoded str."""
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


@dataclass
class FileAttachment:
    """Name/Data mirror the wire shape exactly - a Files list item is always
    {"Name": ..., "Data": ...} on the wire, and asdict(FileAttachment(...))
    produces exactly that (FileName never appears - see below).

    FileName is a constructor-only convenience (a dataclasses.InitVar, not a
    real field - excluded from asdict()/fields()/the wire body) for building
    an attachment from a local file: FileAttachment(FileName="Invoice.pdf")
    or, equivalently, the positional form FileAttachment("Invoice.pdf")
    (FileName is declared first, so it's what a single positional arg maps
    to) reads the file, base64-encodes it into Data, and derives Name from
    the path's basename unless Name is also given explicitly.

    SECURITY: Data is NEVER filesystem-checked, under any circumstances -
    FileAttachment(Name=..., Data=<anything>) always stores Data exactly as
    given. This matters because Data commonly holds content from an external
    source (an HTTP request body, a database blob) that must never be
    reinterpreted as a local file path - a base64 string can coincidentally
    also be a valid, existing filename (base64's alphabet permits any
    all-letter string with a length divisible by 4, e.g. "Makefile", "demo",
    and "requirements" all pass strict base64 validation), so code that ran
    Data through path-detection risked a caller substituting a real
    server-local path and having that file's actual contents silently read
    and attached instead of the literal value they submitted. Only the
    explicit FileName constructor path ever touches the filesystem.
    """

    FileName: InitVar[Optional[str]] = None
    Name: Optional[str] = None
    Data: Optional[str] = None

    def __post_init__(self, FileName):
        if FileName:
            if self.Data is not None:
                raise ValueError("FileAttachment: pass either FileName or Data, not both")
            self.Data = read_file_as_base64(FileName)
            if self.Name is None:
                self.Name = os.path.basename(FileName)


_FILE_ATTACHMENT_FIELD_NAMES = {f.name for f in fields(FileAttachment)}


def resolve_file_field(value):
    """Resolves a value destined for one of Voice's plain str audio fields
    (MessageToPeople, etc.) or AddKeypad's Play arg into a plain base64 str.

    A FileAttachment's .Data is used as-is (already resolved via its own
    __post_init__, e.g. FileAttachment(FileName=...)) - .Name is ignored,
    since these fields have no filename concept. A bare str that is an
    existing local file path is read and base64-encoded - this is the one
    place bare-string path detection still applies to a value that isn't
    wrapped in an explicit FileName= constructor, kept deliberately for
    direct-SDK-call convenience (a developer typing a path literal into
    their own code); it carries the same filesystem-confusion risk described
    on FileAttachment above if a caller instead forwards untrusted/external
    content through this field, so don't do that. Anything else (a bare str
    that isn't a path, or None) passes through unchanged, since these fields
    have always accepted literal base64 directly."""
    if isinstance(value, FileAttachment):
        return value.Data
    if isinstance(value, str) and value and os.path.isfile(value):
        return read_file_as_base64(value)
    return value


def normalize_attachment(value):
    """Mirrors tnzapi.core.destination.normalize_destination(): validates
    and normalizes a single Files list item into a plain dict, or None if
    value doesn't represent an attachment (e.g. None was passed). Raises
    ValueError on an unknown dict key or a bare string that isn't an
    existing file path (there's nowhere else for Name to come from in that
    case).

    A dict's Data is never filesystem-checked - dicts represent the literal
    wire shape ({"Name": ..., "Data": ...}), so only Name/Data are accepted
    keys; FileName is deliberately not a valid dict key (use
    FileAttachment(FileName=...) instead) precisely so a dict's Data can
    never be silently reinterpreted as a path - see FileAttachment's own
    docstring for why that distinction matters.

    A bare non-empty string is treated as a path (kept for direct-SDK-call
    convenience, same as resolve_file_field() - see its docstring for the
    risk this carries if misused with untrusted input) and delegated to
    FileAttachment(FileName=value), raising if it isn't actually an existing
    file. NOTE: this raise is a second line of defense for direct
    normalize_attachment()/AddAttachment() callers - the Set()/SendMessage()
    kwargs path is expected to already have rejected a bad bare string
    earlier, via _first_invalid_field's own Files check, so SendMessage()
    never lets this exception surface."""
    if isinstance(value, FileAttachment):
        return {k: v for k, v in asdict(value).items() if v is not None} or None
    if isinstance(value, dict):
        invalid = next((k for k in value if k not in _FILE_ATTACHMENT_FIELD_NAMES), None)
        if invalid:
            raise ValueError(f"Unknown attachment field: {invalid}")
        return value
    if isinstance(value, str) and value:
        if not os.path.isfile(value):
            raise ValueError(
                f"Files item {value!r} is not an existing file path - a bare string "
                "must be a real file path (Name is derived from its basename); pass "
                "a dict {'Name': ..., 'Data': ...} or FileAttachment for literal "
                "base64 data with an explicit Name."
            )
        return normalize_attachment(FileAttachment(FileName=value))
    return None