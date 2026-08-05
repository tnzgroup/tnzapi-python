# Fax

Send fax documents to one or more recipients via the TNZ REST API.

→ [Common parameters & authentication](../README.md#messaging)

## Quick example

```python
from tnzapi import TNZAPI

client = TNZAPI(AuthToken="[Your Auth Token]")

response = client.Messaging.Fax.SendMessage(
    Destination="+6491232345",
    Files=[{"Name": "Document.pdf", "Data": "<base64-encoded file data>"}]
)

if response.Result == "Success":
    print(f"Success - MessageID: {response.MessageID}")
```

## Parameters (`FaxRequest`)

| Parameter | Type | Required | Description |
|---|---|---|---|
| `Files` | `list[dict]` | Yes‡ | Fax attachments to send — see `AddAttachment(Name, Data)` below. Fax has no `Message` text-body field; the document itself is the payload. |
| `TemplateID` | `str` | Yes‡ | Pre-configured template ID (alternative to `Files`). |
| `Destination` | `str` | Yes* | Single destination shorthand, e.g. `"+6491232345"`. |
| `ToNumber` | `str` | Yes* | Alternative single-destination field. |
| `Destinations` | `list[dict]` | Yes* | One or more destinations — see Destination fields below. |
| `ContactID` | `str` | No | Single addressbook contact to send to (alternative/addition to `Destinations`). |
| `GroupID` | `str` | No | Single addressbook group to send to (alternative/addition to `Destinations`). |
| `MessageID` | `str` | No | Supply your own message ID (otherwise auto-generated). |
| `Reference` | `str` | No | Your internal reference, returned in reports and webhooks. |
| `NotificationType` | `str` | No | Notification delivery mode. |
| `WebhookCallbackURL` | `str` | No | URL for delivery status callbacks. |
| `WebhookCallbackFormat` | `str` | No | Callback format (`JSON`/`XML`/`POST`/`GET`). |
| `ReportTo` | `str` | No | Email address to receive delivery reports. |
| `SendTime` | `str` | No | Schedule delivery — combine with `Timezone`. |
| `Timezone` | `str` | No | Timezone name for `SendTime` (e.g. `"New Zealand"`, `"Pacific/Auckland"`). |
| `SubAccount` | `str` | No | Sub-account code for billing separation. |
| `Department` | `str` | No | Department code. |
| `CSID` | `str` | No | Called Subscriber ID string shown on the recipient fax machine/header. |
| `Resolution` | `str` | No | Fax resolution, e.g. `"Fine"`. |
| `WatermarkFolder` | `str` | No | Folder containing the watermark image/template to stamp onto pages. |
| `WatermarkFirstPage` | `str` | No | Watermark text/token to stamp onto the first page only. |
| `WatermarkAllPages` | `str` | No | Watermark text/token to stamp onto every page, e.g. `"Page [[PageNumber]]"`. |
| `RetryAttempts` | `int` | No | Number of retry attempts on send failure (busy/no answer/fax error). |
| `RetryPeriod` | `int` | No | Minutes to wait between retry attempts. |
| `Mode` | `str` | No | Set `"Test"` to validate without sending. Default `"Live"`. Also accepts the typed `SendMode` enum (`SendMode.Test`/`SendMode.Live`) - see [Send Mode reference](../README.md#send-mode-reference). |

\*Set via `Destination`/`ToNumber`/`Destinations`, or via `AddDestination(...)` on the builder.
‡Either `Files` or `TemplateID` must be provided.

## Destination fields (`Destinations` list items)

| Field | Description |
|---|---|
| `ToNumber` | Destination fax number, e.g. `"+6491232345"`. |
| `Recipient` | Generic destination address, sent as-is regardless of channel — same effect as `ToNumber` here. |
| `FaxNumber` | Alternative phone field, same effect as `ToNumber` for this channel. |
| `MobilePhone` | Accepted but not read by Fax (used by SMS/WhatsApp/RCS). |
| `MainPhone` | Accepted but not read by Fax (used by TTS/Voice). |
| `EmailAddress` | Accepted but not read by Fax (used by Email). |
| `ContactID` | Addressbook contact reference — sends to that contact instead of a raw number. |
| `GroupID` | Addressbook group reference — sends to all members of that group. |
| `GroupCode` | Alternative group lookup by code (instead of `GroupID`). |
| `FirstName` / `LastName` / `Company` / `Attention` | Not rendered into a merge tag (Fax has no message body) — still accepted on the destination and echoed back in status reports, for your own reference. |
| `Custom1`–`Custom9` | Same as above — reference-only, not rendered into anything, but echoed back in status reports. |

A `tnzapi.core.destination.Destination` instance can be used instead of a raw dict — it validates
field names at construction time (`Destination(ToNumber="...", Bogus="...")` raises `TypeError`),
and an unknown key in a raw dict is now rejected the same way (`ValueError` for `Set()`/
`AddDestination()`, `Result="Failed"` for `SendMessage()`).

## Attachment fields (`Files` list items)

`Files` accepts any mix of three shapes in the same list:

| Shape | Example | Notes |
|---|---|---|
| Bare file path string | `"Invoice.pdf"` | `Name` is derived from the path's basename. Raises `ValueError` if the path doesn't exist — there's no separate field to supply a filename otherwise. |
| `{"Name": ..., "Data": ...}` dict | `{"Name": "Invoice.pdf", "Data": "<base64>"}` | `Data` is always literal base64 — never filesystem-checked, even if it happens to look like a path (see the security note below). |
| `FileAttachment(...)` instance | `FileAttachment("Invoice.pdf")` | See below. |

`tnzapi.core.file_attachment.FileAttachment` mirrors `Destination`: a plain dataclass (`Name`, `Data`)
usable with `AddAttachment(...)` or directly in `Files=[...]`. `FileAttachment(<path>)` — a single
positional argument, equivalently `FileAttachment(FileName=<path>)` — reads the file and base64-encodes it
automatically, deriving `Name` from the path's basename unless overridden (e.g.
`FileAttachment(<path>, Name="Custom.pdf")`).

**`Data` is never filesystem-checked, under any circumstances.** `FileAttachment(Name=..., Data=<anything>)`
and a `{"Name": ..., "Data": ...}` dict both always store `Data` exactly as given — this matters whenever
`Data` comes from an external source (e.g. an HTTP request body), since a base64 string can coincidentally
also be a valid, existing local filename. Only the explicit `FileName=`/positional-path form ever reads
from disk.

## Code samples

### Flat kwargs

```python
response = client.Messaging.Fax.SendMessage(
    Destination="+6491232345",
    Files=[{"Name": "Document.pdf", "Data": "<base64-encoded file data>"}]
)
```

### Builder

```python
response = (
    client.Messaging.Fax
    .Set()
    .AddDestination("+6491232345")
    .AddAttachment("path/to/doc.pdf")
    .SendMessage()
)
```

### From a file path

A bare path string is read and base64-encoded automatically — no manual `base64` handling needed:

```python
response = (
    client.Messaging.Fax
    .Set()
    .AddDestination("+6491232345")
    .AddAttachment("MyDocument.pdf")
    .SendMessage()
)
```

### Using the typed `FileAttachment`

```python
from tnzapi.core.file_attachment import FileAttachment

response = (
    client.Messaging.Fax
    .Set()
    .AddDestination("+6491232345")
    .AddAttachment(
        FileAttachment("path/to/doc.pdf")
    )
    .SendMessage()
)
```

### Multiple pages, via `AddAttachments`

`AddAttachments([...])` adds several attachments (e.g. a fax with multiple pages sent as separate files)
in one call - each item can be a path string, a `{"Name": ..., "Data": ...}` dict, or a `FileAttachment`
instance, mixed freely in the same list.

```python
response = (
    client.Messaging.Fax
    .Set()
    .AddDestination("+6491232345")
    .AddAttachments(["path/to/page1.pdf", "path/to/page2.pdf"])
    .SendMessage()
)
```

### Addressbook destination

```python
response = (
    client.Messaging.Fax
    .Set()
    .AddAttachment("path/to/doc.pdf")
    .AddDestination(ContactID="[Contact ID]")
    .AddDestination(GroupID="[Group ID]")
    .SendMessage()
)
```

### Multiple recipients

```python
response = client.Messaging.Fax.SendMessage(
    Destinations=[
        {"ToNumber": "+6491232345"},
        {"ToNumber": "+6491232346"},
    ],
    Files=[{"Name": "Document.pdf", "Data": "<base64-encoded file data>"}],
)
```

### Multiple recipients, via typed `Destination`

```python
from tnzapi.core.destination import Destination

response = client.Messaging.Fax.SendMessage(
    Destinations=[
        Destination("+6491232345"),
        Destination("+6491232346"),
    ],
    Files=[{"Name": "Document.pdf", "Data": "<base64-encoded file data>"}],
)
```

### Multiple recipients, via `AddDestinations`

`AddDestinations([...])` adds several destinations in one call on the builder - each item can be a bare
string, a dict, or a typed `Destination`, mixed freely in the same list. Unlike `AddDestination(...)`
(singular), which only ever adds one destination per call and raises `TypeError` on a list, this is the
chainable way to add several at once.

```python
response = (
    client.Messaging.Fax
    .Set()
    .AddAttachment("path/to/doc.pdf")
    .AddDestinations(["+6491232345", "+6491232346"])
    .SendMessage()
)
```

### With reference fields

Fax has no message body, so `Company`/`Attention`/`Custom1`–`Custom9` on a destination are never rendered
into anything — but they're still accepted and echoed back in status reports, for your own reference.

```python
from tnzapi.core.destination import Destination

response = client.Messaging.Fax.SendMessage(
    Destinations=[
        Destination(
            FaxNumber="+6491232345",
            Attention="Accounts Payable",
            Custom1="Invoice #1234",
        ),
    ],
    Files=[{"Name": "Invoice.pdf", "Data": "<base64-encoded file data>"}],
)
```

### Bulk send with per-destination reference fields, via `AddDestinations`

Fax has no message body to personalise, but reference fields are still accepted per-destination and
echoed back in status reports.

```python
from tnzapi.core.destination import Destination

response = (
    client.Messaging.Fax
    .Set()
    .AddAttachment("path/to/doc.pdf")
    .AddDestinations([
        Destination(
            FaxNumber="+6491232345",
            Attention="Accounts Payable",
            Custom1="Invoice #1234",
        ),
        Destination(
            FaxNumber="+6491232346",
            Attention="Purchasing",
            Custom1="Invoice #1235",
        ),
    ])
    .SendMessage()
)
```

### Scheduled send

```python
response = client.Messaging.Fax.SendMessage(
    Destination="+6491232345",
    Files=[{"Name": "Document.pdf", "Data": "<base64-encoded file data>"}],
    SendTime="2026-08-01T09:00:00",
    Timezone="Pacific/Auckland",
)
```

### CSID, resolution, retry and watermark

```python
response = client.Messaging.Fax.SendMessage(
    Destination="+6491232345",
    Files=[{"Name": "Document.pdf", "Data": "<base64-encoded file data>"}],
    CSID="TNZ Group",
    Resolution="Fine",
    RetryAttempts=3,
    RetryPeriod=15,
    WatermarkFolder="Invoices",
    WatermarkFirstPage="CONFIDENTIAL",
    WatermarkAllPages="Page [[PageNumber]]",
)
```

### Test mode (validate without sending)

`Mode` also accepts the typed `SendMode` enum as an equivalent alternative to the plain string -
`Mode=SendMode.Test` and `Mode="Test"` are fully interchangeable:

```python
from tnzapi.core.send_mode import SendMode

response = (
    client.Messaging.Fax
    .Set(
        Mode=SendMode.Test
    )
    .AddDestination("+6491232345")
    .AddAttachment("path/to/doc.pdf")
    .SendMessage()
)
```

### Poll for status

```python
status = client.Messaging.Fax.Status(MessageID=response.MessageID)

if status.Result == "Success":
    print(f"JobStatus: {status.JobStatus}")
    for recipient in status.Recipients:
        print(f" -> {recipient}")
```

### Reschedule / Abort / Resubmit

```python
client.Messaging.Fax.Reschedule(
    MessageID=response.MessageID,
    SendTime="2026-08-01T09:00:00",
)
client.Messaging.Fax.Abort(MessageID=response.MessageID)
client.Messaging.Fax.Resubmit(
    MessageID=response.MessageID,
    SendTime="2026-08-01T09:00:00",
)
```

Fax has no `Received`/`Pacing` (`Received` exists on SMS/WhatsApp/RCS only; `Pacing` on TTS/Voice only).

## Response

- `SendMessage(...)` → `FaxResponse`: `Result`, `MessageID`, `ErrorMessage`.
- `Status(...)` → `FaxStatus`: `Result`, `MessageID`, `JobStatus`, `JobNum`, `Account`, `SubAccount`, `Department`, `Reference`, `CreatedTimeLocal`/`CreatedTimeUTC`/`CreatedTimeUTC_RFC3339`, `DelayedTimeLocal`/`DelayedTimeUTC`/`DelayedTimeUTC_RFC3339`, `Timezone`, `Count`, `Complete`, `Success`, `Failed`, `Price`, `Recipients`, `TotalRecords`/`RecordsPerPage`/`PageCount`/`Page`, `ErrorMessage`.
- `Reschedule(...)`/`Abort(...)`/`Resubmit(...)` → `FaxActionResult`: `Result`, `ActionResult`, `MessageID`, `JobNum`, `Status`, `Action`, `ErrorMessage`.

`FaxResponse`/`FaxStatus`/`FaxActionResult` were named `...DTO` before this SDK's public response types dropped that internal-architecture suffix; the old names still work (they emit a `DeprecationWarning`) — see [messaging.md](messaging.md#response-shape).

### Recipient dict (each entry in `Status(...)`'s `Recipients`)

Fax's `Recipients` entries are plain `dict`s, not typed objects — access fields with
`recipient["Field"]`/`recipient.get("Field")`, not attribute access.

| Key | Description |
|---|---|
| `Type` | Recipient channel type. |
| `DestSeq` | TNZ's internal sequence ID for this recipient within the job. |
| `Destination` | The recipient's fax number. |
| `ContactID` | Addressbook contact reference, if sent via `ContactID`/`GroupID`. |
| `Status` | Delivery status for this recipient. |
| `Result` | Human-readable delivery result for this recipient. |
| `SentTimeLocal` / `SentTimeUTC` / `SentTimeUTC_RFC3339` | When the message was actually sent to this recipient. |
| `Attention` / `Company` / `Custom1`–`Custom9` | Echoed reference fields — see Destination fields above. |
| `RemoteID` | Carrier/network-assigned identifier for this delivery, if available. |
| `Price` | Per-recipient cost. |

## See also

- [README — Fax](../README.md#fax)
- [Samples — fax_samples.py](../samples/messaging/fax_samples.py)
