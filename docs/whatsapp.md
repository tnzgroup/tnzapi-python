# WhatsApp

Send WhatsApp template messages to one or more recipients via the TNZ REST API.

→ [Common parameters & authentication](../README.md#messaging)

WhatsApp requires an approved `TemplateID` and a `FromNumber` (your registered WhatsApp sender number) on every send — the message content must exactly match the content of the approved template.

**Strict client-side validation:** unlike every other channel, `WhatsApp.SendMessage(...)` pre-checks
`TemplateID`/`Message`/`FromNumber` (and that a destination is present) client-side, *before* making any
HTTP call — a missing field returns `Result="Failed"` with `ErrorMessage=["Missing required field: <name>"]`
immediately, without contacting the TNZ API at all.

## Quick example

```python
from tnzapi import TNZAPI

client = TNZAPI(AuthToken="[Your Auth Token]")

response = client.Messaging.WhatsApp.SendMessage(
    TemplateID="[Your Template ID]",
    Message="Hi there!",
    FromNumber="+6495006000",
    Destination="+64211234567"
)

if response.Result == "Success":
    print(f"Success - MessageID: {response.MessageID}")
```

## Parameters (`WhatsAppRequest`)

| Parameter | Type | Required | Description |
|---|---|---|---|
| `TemplateID` | `str` | Yes | Pre-approved WhatsApp message template ID assigned to your account. |
| `Message` | `str` | Yes | Message body. Must exactly match the content of the approved `TemplateID` template. |
| `FallbackMode` | `str \| list[str]` | No | Fallback channel(s) if WhatsApp delivery fails, tried in the order given, e.g. `"SMS"` or `["SMS", "RCS"]`. A list is joined into TNZ's wire format automatically (`"SMS, RCS"`). |
| `Files` | `list[dict]` | No | Attachments — see `AddAttachment(Name, Data)` below. |
| `FromNumber` | `str` | Yes | Your registered WhatsApp sender number, e.g. `"+6495006000"`. |
| `Destination` | `str` | Yes† | Single destination shorthand, e.g. `"+64211231234"`. |
| `ToNumber` | `str` | Yes† | Alternative single-destination field. |
| `Destinations` | `list[dict]` | Yes† | One or more destinations — see Destination fields below. |
| `ContactID` | `str` | No | Single addressbook contact to send to (alternative/addition to `Destinations`). |
| `GroupID` | `str` | No | Single addressbook group to send to (alternative/addition to `Destinations`). |
| `MessageID` | `str` | No | Supply your own message ID (otherwise auto-generated). |
| `Reference` | `str` | No | Your internal reference, returned in reports and webhooks. |
| `NotificationType` | `str` | No | Notification delivery mode. |
| `WebhookCallbackURL` | `str` | No | URL for delivery status callbacks. |
| `WebhookCallbackFormat` | `str` | No | Callback format (`JSON`/`XML`/`POST`/`GET`). |
| `SendTime` | `str` | No | Schedule delivery — combine with `Timezone`. |
| `Timezone` | `str` | No | Timezone name for `SendTime` (e.g. `"New Zealand"`, `"Pacific/Auckland"`). |
| `SubAccount` | `str` | No | Sub-account code for billing separation. |
| `Department` | `str` | No | Department code. |
| `Mode` | `str` | No | Set `"Test"` to validate without sending. Default `"Live"`. Also accepts the typed `SendMode` enum (`SendMode.Test`/`SendMode.Live`) - see [Send Mode reference](../README.md#send-mode-reference). |

`TemplateID`, `Message`, and `FromNumber` are all required — unlike SMS, there is no `Message`/`TemplateID` either/or.
†Set via `Destination`/`ToNumber`/`Destinations`, or via `AddDestination(...)` on the builder.

## Destination fields (`Destinations` list items)

| Field | Description |
|---|---|
| `ToNumber` | Destination phone number, e.g. `"+64211111111"`. |
| `Recipient` | Generic destination address, sent as-is regardless of channel — same effect as `ToNumber` here. |
| `MobilePhone` | Alternative phone field, same effect as `ToNumber` for this channel. |
| `MainPhone` | Accepted but not read by WhatsApp (used by TTS/Voice). |
| `EmailAddress` | Accepted but not read by WhatsApp (used by Email). |
| `FaxNumber` | Accepted but not read by WhatsApp (used by Fax). |
| `ContactID` | Addressbook contact reference — sends to that contact instead of a raw number. |
| `GroupID` | Addressbook group reference — sends to all members of that group. |
| `GroupCode` | Alternative group lookup by code (instead of `GroupID`). |
| `FirstName` / `LastName` / `Company` / `Attention` | Personalisation tokens, e.g. `[[FirstName]]`. |
| `Custom1`–`Custom9` | Arbitrary per-recipient personalisation values, `[[Custom1]]` … `[[Custom9]]`. |

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
response = client.Messaging.WhatsApp.SendMessage(
    TemplateID="[Your Template ID]",
    Message="Hi there!",
    FromNumber="+6495006000",
    Destination="+64211234567"
)
```

### Builder

```python
response = (
    client.Messaging.WhatsApp
    .Set(
        TemplateID="[Your Template ID]",
        Message="Hi there!",
        FromNumber="+6495006000",
    )
    .AddDestination("+64211234567")
    .SendMessage()
)
```

### Addressbook destination

```python
response = (
    client.Messaging.WhatsApp
    .Set(
        TemplateID="[Your Template ID]",
        Message="Hi [[FirstName]]!",
        FromNumber="+6495006000",
    )
    .AddDestination(ContactID="[Contact ID]")
    .AddDestination(GroupID="[Group ID]")
    .SendMessage()
)
```

### Multiple recipients

```python
response = client.Messaging.WhatsApp.SendMessage(
    TemplateID="[Your Template ID]",
    Message="Hi there!",
    FromNumber="+6495006000",
    Destinations=[
        {"ToNumber": "+64211234567"},
        {"ToNumber": "+64211234568"},
    ],
)
```

### Multiple recipients, via typed `Destination`

```python
from tnzapi.core.destination import Destination

response = (
    client.Messaging.WhatsApp
    .Set(
        TemplateID="[Your Template ID]",
        Message="Hi [[FirstName]]!",
        FromNumber="+6495006000",
    )
    .AddDestinations([
        Destination(ToNumber="+64211234567", FirstName="Alice"),
        Destination(ToNumber="+64211234568", FirstName="Bob"),
    ])
    .SendMessage()
)
```

### Multiple recipients, via `AddDestinations`

`AddDestinations([...])` adds several destinations in one call on the builder - each item can be a bare
string, a dict, or a typed `Destination`, mixed freely in the same list. Unlike `AddDestination(...)`
(singular), which only ever adds one destination per call and raises `TypeError` on a list, this is the
chainable way to add several at once.

```python
response = (
    client.Messaging.WhatsApp
    .Set(
        TemplateID="[Your Template ID]",
        Message="Hi [[FirstName]]!",
        FromNumber="+6495006000",
    )
    .AddDestinations([
        "+64211234567",
        {"ToNumber": "+64211234568", "FirstName": "Bob"},
    ])
    .SendMessage()
)
```

### With SMS fallback

```python
response = client.Messaging.WhatsApp.SendMessage(
    TemplateID="[Your Template ID]",
    Message="Hi there!",
    FromNumber="+6495006000",
    Destination="+64211234567",
    FallbackMode="SMS",
)
```

### With attachment

```python
response = (
    client.Messaging.WhatsApp
    .Set(
        TemplateID="[Your Template ID]",
        Message="See the attached document.",
        FromNumber="+6495006000",
    )
    .AddDestination("+64211234567")
    .AddAttachment("path/to/doc.pdf")
    .SendMessage()
)
```

### With attachment, from a file path or via typed `FileAttachment`

```python
from tnzapi.core.file_attachment import FileAttachment

response = (
    client.Messaging.WhatsApp
    .Set(
        TemplateID = "[Your Template ID]",
        Message = "See the attached document.",
        FromNumber = "+6495006000",
    )
    .AddDestination("+64211234567")
    .AddAttachment(
        FileAttachment("path/to/doc.pdf")
    )
    .SendMessage()
)
```

### Multiple attachments, via `AddAttachments`

`AddAttachments([...])` adds several attachments in one call - each item can be a path string, a
`{"Name": ..., "Data": ...}` dict, or a `FileAttachment` instance, mixed freely in the same list.

```python
response = (
    client.Messaging.WhatsApp
    .Set(
        TemplateID="[Your Template ID]",
        Message="See the attached documents.",
        FromNumber="+6495006000",
    )
    .AddDestination("+64211234567")
    .AddAttachments(["path/to/doc.pdf", "path/to/receipt.pdf"])
    .SendMessage()
)
```

### Test mode (validate without sending)

`Mode` also accepts the typed `SendMode` enum as an equivalent alternative to the plain string -
`Mode=SendMode.Test` and `Mode="Test"` are fully interchangeable:

```python
from tnzapi.core.send_mode import SendMode

response = (
    client.Messaging.WhatsApp
    .Set(
        TemplateID="[Your Template ID]",
        Message="Hi there!",
        FromNumber="+6495006000",
        Mode=SendMode.Test
    )
    .AddDestination("+64211234567")
    .SendMessage()
)
```

### Poll for status

```python
status = client.Messaging.WhatsApp.Status(MessageID=response.MessageID)

if status.Result == "Success":
    print(f"JobStatus: {status.JobStatus}")
    for recipient in status.Recipients:
        print(f" -> {recipient}")
```

### Poll for inbound WhatsApp

```python
received = client.Messaging.WhatsApp.Received(TimePeriod=1440)  # minutes

if received.Result == "Success":
    for message in received.Messages:
        print(message)
```

`Received(...)` only ever returns the requested page — it never auto-walks every page on your behalf. See `samples/messaging/_pagination.py`'s `WalkAllPages` helper if you need to walk everything.

### Reschedule / Abort

```python
client.Messaging.WhatsApp.Reschedule(
    MessageID=response.MessageID,
    SendTime="2026-08-01T09:00:00",
)
client.Messaging.WhatsApp.Abort(MessageID=response.MessageID)
```

WhatsApp has no `Resubmit`/`Pacing` (those exist on Email/Fax/TTS/Voice — `Pacing` on TTS/Voice only).

## Response

- `SendMessage(...)` → `WhatsAppResponse`: `Result`, `MessageID`, `ErrorMessage`.
- `Status(...)` → `WhatsAppStatus`: `Result`, `MessageID`, `JobStatus`, `JobNum`, `Account`, `SubAccount`, `Department`, `Reference`, `CreatedTimeLocal`/`CreatedTimeUTC`/`CreatedTimeUTC_RFC3339`, `DelayedTimeLocal`/`DelayedTimeUTC`/`DelayedTimeUTC_RFC3339`, `Timezone`, `Count`, `Complete`, `Success`, `Failed`, `Price`, `Recipients`, `TotalRecords`/`RecordsPerPage`/`PageCount`/`Page`, `ErrorMessage`.
- `Received(...)` → `WhatsAppReceived`: `Result`, `Messages`, `TotalRecords`/`RecordsPerPage`/`PageCount`/`Page`, `ErrorMessage`.
- `Reschedule(...)`/`Abort(...)` → `WhatsAppActionResult`: `Result`, `ActionResult`, `MessageID`, `JobNum`, `Status`, `Action`, `ErrorMessage`.

`WhatsAppResponse`/`WhatsAppStatus`/`WhatsAppActionResult`/`WhatsAppReceived` were named `...DTO` before this SDK's public response types dropped that internal-architecture suffix; the old names still work (they emit a `DeprecationWarning`) — see [messaging.md](messaging.md#response-shape).

### Recipient dict (each entry in `Status(...)`'s `Recipients`)

WhatsApp's `Recipients` entries are plain `dict`s, not typed objects — access fields with
`recipient["Field"]`/`recipient.get("Field")`, not attribute access.

| Key | Description |
|---|---|
| `Type` | Recipient channel type. |
| `DestSeq` | TNZ's internal sequence ID for this recipient within the job. |
| `Destination` | The recipient's phone number. |
| `ContactID` | Addressbook contact reference, if sent via `ContactID`/`GroupID`. |
| `Status` | Delivery status for this recipient. |
| `Result` | Human-readable delivery result for this recipient. |
| `SentTimeLocal` / `SentTimeUTC` / `SentTimeUTC_RFC3339` | When the message was actually sent to this recipient. |
| `Attention` / `Company` / `Custom1`–`Custom9` | Echoed personalisation fields — see Destination fields above. |
| `RemoteID` | Carrier/network-assigned identifier for this delivery, if available. |
| `Price` | Per-recipient cost. |
| `SMSReplies` | Inbound replies attached to this recipient. The key is named `SMSReplies` even on WhatsApp — it isn't a mistake in this doc, it's the wire API's own field name, shared across channels. |

## See also

- [README — WhatsApp](../README.md#whatsapp)
- [Samples — whatsapp_samples.py](../samples/messaging/whatsapp_samples.py)
