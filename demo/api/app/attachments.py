import base64
import binascii

# Reference-implementation limits, not values the real TNZ API enforces (that's server-side and
# unknown to this demo) - just enough to stop an accidental huge/numerous upload from exhausting
# this process's memory before ever reaching the network.
MAX_ATTACHMENT_SIZE_BYTES = 10 * 1024 * 1024  # 10 MiB of decoded content per attachment
MAX_ATTACHMENT_COUNT = 20


def validate_file_content(value: str) -> str:
    # Fast pre-check on the encoded length before paying for a full decode - base64 inflates
    # size by 4/3 (+ up to 4 bytes of padding), so anything within that bound could plausibly
    # still be under the limit and needs the real decode below; anything past it cannot be,
    # and rejecting it here avoids allocating the full decoded buffer just to discard it.
    if len(value) > MAX_ATTACHMENT_SIZE_BYTES * 4 // 3 + 4:
        raise ValueError(
            f"FileContent encoded length implies more than {MAX_ATTACHMENT_SIZE_BYTES} decoded bytes."
        )

    try:
        decoded_length = len(base64.b64decode(value, validate=True))
    except (binascii.Error, ValueError) as exc:
        raise ValueError(f"FileContent is not valid base64: {exc}") from None

    if decoded_length > MAX_ATTACHMENT_SIZE_BYTES:
        raise ValueError(
            f"FileContent decodes to {decoded_length} bytes, exceeding the "
            f"{MAX_ATTACHMENT_SIZE_BYTES}-byte reference-implementation limit."
        )

    return value


def validate_attachment_count(value):
    if value is not None and len(value) > MAX_ATTACHMENT_COUNT:
        raise ValueError(
            f"{len(value)} attachments given, exceeding the {MAX_ATTACHMENT_COUNT}-attachment "
            "reference-implementation limit."
        )
    return value


# Applied via `_file_content_validator = field_validator("FileContent")(validate_file_content)`
# on each MessageAttachment model - a plain function reused across routers rather than a shared
# base class, since Pydantic field_validator must be bound per-model.
