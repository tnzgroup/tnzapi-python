# Email

Send email messages (plain text and/or HTML, with attachments) to one or more recipients via the TNZ REST API.

→ [Common parameters & authentication](../README.md#messaging)

## Quick example

```python
from tnzapi import TNZAPI

client = TNZAPI(AuthToken="[Your Auth Token]")

response = client.Messaging.Email.SendMessage(
    EmailSubject="Test Email",
    MessagePlain="Hi world!",
    Destination="recipient@example.com"
)

if response.Result == "Success":
    print(f"Success - MessageID: {response.MessageID}")
```

## Parameters (`EmailRequest`)

| Parameter | Type | Required | Description |
|---|---|---|---|
| `MessagePlain` | `str` | Yes* | Plain-text email body. Supports personalisation tokens `[[FirstName]]`, `[[Custom1]]`, etc. |
| `MessageHTML` | `str` | Yes* | HTML email body. Can be used together with `MessagePlain` (a multipart email), or on its own. |
| `TemplateID` | `str` | Yes* | Pre-configured dashboard template ID (alternative to `MessagePlain`/`MessageHTML`). |
| `Destination` | `str` | Yes† | Single destination shorthand, e.g. `"recipient@example.com"`. |
| `EmailAddress` | `str` | Yes† | Alternative single-destination field. |
| `Destinations` | `list[dict]` | Yes† | One or more destinations — see Destination fields below. |
| `ContactID` | `str` | No | Single addressbook contact to send to (alternative/addition to `Destinations`). |
| `GroupID` | `str` | No | Single addressbook group to send to (alternative/addition to `Destinations`). |
| `MessageID` | `str` | No | Supply your own message ID (otherwise auto-generated). |
| `Reference` | `str` | No | Your internal reference, returned in reports and webhooks. |
| `From` | `str` | No | Sender's friendly (display) name, as seen by the email recipient. |
| `FromEmail` | `str` | No | Sender's email address. Uses your API user's default address if not specified. |
| `CCEmail` | `str` | No | Tracked CC address added to the email (chargeable, per recipient). |
| `BCCEmail` | `str` | No | Untracked BCC address added to the email (chargeable, per recipient). |
| `ReplyTo` | `str` | No | Reply-To address — replies from the recipient are sent here instead of `FromEmail`. |
| `EmailSubject` | `str` | No | Subject line for the email. |
| `NotificationType` | `str` | No | Notification delivery mode. |
| `WebhookCallbackURL` | `str` | No | URL for delivery status callbacks. |
| `WebhookCallbackFormat` | `str` | No | Callback format (`JSON`/`XML`/`POST`/`GET`). |
| `ReportTo` | `str` | No | Email address to receive delivery reports. |
| `SendTime` | `str` | No | Schedule delivery — combine with `Timezone`. |
| `Timezone` | `str` | No | Timezone name for `SendTime` (e.g. `"New Zealand"`, `"Pacific/Auckland"`). |
| `SubAccount` | `str` | No | Sub-account code for billing separation. |
| `Department` | `str` | No | Department code. |
| `Files` | `list[dict]` | No | Attachments — see `AddAttachment(Name, Data)` below. |
| `Mode` | `str` | No | Set `"Test"` to validate without sending. Default `"Live"`. Also accepts the typed `SendMode` enum (`SendMode.Test`/`SendMode.Live`) - see [Send Mode reference](../README.md#send-mode-reference). |

\*At least one of `MessagePlain`, `MessageHTML`, or `TemplateID` must be provided. `MessagePlain` and `MessageHTML` may be combined to send a multipart email.
†Set via `Destination`/`EmailAddress`/`Destinations`, or via `AddDestination(...)` on the builder.

## Destination fields (`Destinations` list items)

| Field | Description |
|---|---|
| `EmailAddress` | Destination email address, e.g. `"recipient@example.com"`. |
| `Recipient` | Generic destination address, sent as-is regardless of channel — same effect as `EmailAddress` here. |
| `ToNumber` | Accepted but not read by Email (used by SMS/Fax/TTS/Voice/WhatsApp/RCS). |
| `MobilePhone` | Accepted but not read by Email (used by SMS/WhatsApp/RCS). |
| `MainPhone` | Accepted but not read by Email (used by TTS/Voice). |
| `FaxNumber` | Accepted but not read by Email (used by Fax). |
| `ContactID` | Addressbook contact reference — sends to that contact instead of a raw address. |
| `GroupID` | Addressbook group reference — sends to all members of that group. |
| `GroupCode` | Alternative group lookup by code (instead of `GroupID`). |
| `FirstName` / `LastName` / `Company` / `Attention` | Personalisation tokens, e.g. `[[FirstName]]`. |
| `Custom1`–`Custom9` | Arbitrary per-recipient personalisation values, `[[Custom1]]` … `[[Custom9]]`. |

A `tnzapi.core.destination.Destination` instance can be used instead of a raw dict — it validates
field names at construction time (`Destination(EmailAddress="...", Bogus="...")` raises `TypeError`),
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
response = client.Messaging.Email.SendMessage(
    EmailSubject="Test Email",
    MessagePlain="Hi world!",
    Destination="recipient@example.com"
)
```

### Builder

```python
response = (
    client.Messaging.Email
    .Set(
        EmailSubject="Test Email",
        MessagePlain="Hi world!"
    )
    .AddDestination("recipient@example.com")
    .SendMessage()
)
```

### Addressbook destination

```python
response = (
    client.Messaging.Email
    .Set(
        EmailSubject="Test Email",
        MessagePlain="Hi [[FirstName]]!",
    )
    .AddDestination(ContactID="[Contact ID]")
    .AddDestination(GroupID="[Group ID]")
    .SendMessage()
)
```

### Multiple contacts and groups

```python
response = client.Messaging.Email.SendMessage(
    EmailSubject="Test Email",
    MessagePlain="Hi [[FirstName]]!",
    Destinations=[
        {"ContactID": "[Contact ID 1]"},
        {"ContactID": "[Contact ID 2]"},
        {"GroupID": "[Group ID 1]"},
        {"GroupID": "[Group ID 2]"},
    ],
)
```

### Multiple contacts and groups, via typed `Destination`

```python
from tnzapi.core.destination import Destination

response = client.Messaging.Email.SendMessage(
    EmailSubject="Test Email",
    MessagePlain="Hi [[FirstName]]!",
    Destinations=[
        Destination(ContactID="[Contact ID 1]"),
        Destination(ContactID="[Contact ID 2]"),
        Destination(GroupID="[Group ID 1]"),
        Destination(GroupID="[Group ID 2]"),
    ],
)
```

### Multiple recipients, via `AddDestinations`

`AddDestinations([...])` adds several destinations in one call on the builder - each item can be a bare
string, a dict, or a typed `Destination`, mixed freely in the same list. Unlike `AddDestination(...)`
(singular), which only ever adds one destination per call and raises `TypeError` on a list, this is the
chainable way to add several at once.

```python
response = (
    client.Messaging.Email
    .Set(EmailSubject="Test Email", MessagePlain="Hi [[FirstName]]!")
    .AddDestinations([
        "recipient@example.com",
        {"EmailAddress": "bob@example.com", "FirstName": "Bob"},
    ])
    .SendMessage()
)
```

### Bulk send with per-destination personalisation, via typed `Destination`

```python
from tnzapi.core.destination import Destination

response = (
    client.Messaging.Email
    .Set(
        EmailSubject="Test Email",
        MessagePlain="Hi [[FirstName]], your appointment is on [[Custom1]]."
    )
    .AddDestinations([
        Destination(
            EmailAddress="alice@example.com",
            FirstName="Alice",
            Custom1="Monday 3pm",
        ),
        Destination(
            EmailAddress="bob@example.com",
            FirstName="Bob",
            Custom1="Tuesday 10am",
        ),
    ])
    .SendMessage()
)
```

### HTML email

```python
response = client.Messaging.Email.SendMessage(
    EmailSubject="Test Email",
    MessageHTML="<h1>Hi world!</h1><p>This is an HTML email.</p>",
    Destination="recipient@example.com",
)
```

### With attachment

```python
response = (
    client.Messaging.Email
    .Set(
        EmailSubject="Test Email with Attachment",
        MessagePlain="See the attached document.",
    )
    .AddDestination("recipient@example.com")
    .AddAttachment("path/to/doc.pdf")
    .SendMessage()
)
```

### With attachment, from a file path or via typed `FileAttachment`

```python
from tnzapi.core.file_attachment import FileAttachment

response = (
    client.Messaging.Email
    .Set(
        EmailSubject = "Test Email with Attachment",
        MessagePlain = "See the attached document.",
    )
    .AddDestination("recipient@example.com")
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
    client.Messaging.Email
    .Set(
        EmailSubject="Test Email with Attachments",
        MessagePlain="See the attached documents.",
    )
    .AddDestination("recipient@example.com")
    .AddAttachments(["path/to/doc.pdf", "path/to/invoice.pdf"])
    .SendMessage()
)
```

### Custom sender, reply-to, and CC

```python
response = client.Messaging.Email.SendMessage(
    EmailSubject="Test Email",
    MessagePlain="Hi world!",
    Destination="recipient@example.com",
    From="Support Team",
    FromEmail="support@example.com",
    ReplyTo="replies@example.com",
    CCEmail="manager@example.com",
)
```

### Test mode (validate without sending)

`Mode` also accepts the typed `SendMode` enum as an equivalent alternative to the plain string -
`Mode=SendMode.Test` and `Mode="Test"` are fully interchangeable:

```python
from tnzapi.core.send_mode import SendMode

response = (
    client.Messaging.Email
    .Set(
        EmailSubject="Test Email",
        MessagePlain="Hi world!",
        Mode=SendMode.Test
    )
    .AddDestination("recipient@example.com")
    .SendMessage()
)
```

### Poll for status

```python
status = client.Messaging.Email.Status(MessageID=response.MessageID)

if status.Result == "Success":
    print(f"JobStatus: {status.JobStatus}")
    for recipient in status.Recipients:
        print(f" -> {recipient}")
```

### Reschedule / Abort / Resubmit

```python
client.Messaging.Email.Reschedule(
    MessageID=response.MessageID,
    SendTime="2026-08-01T09:00:00",
)
client.Messaging.Email.Abort(MessageID=response.MessageID)
client.Messaging.Email.Resubmit(
    MessageID=response.MessageID,
    SendTime="2026-08-01T09:00:00",
)
```

Email has no `Received`/`Pacing` (`Received` exists on SMS/WhatsApp/RCS only; `Pacing` on TTS/Voice only).

## Response

- `SendMessage(...)` → `EmailResponse`: `Result`, `MessageID`, `ErrorMessage`.
- `Status(...)` → `EmailStatus`: `Result`, `MessageID`, `JobStatus`, `JobNum`, `Account`, `SubAccount`, `Department`, `Reference`, `CreatedTimeLocal`/`CreatedTimeUTC`/`CreatedTimeUTC_RFC3339`, `DelayedTimeLocal`/`DelayedTimeUTC`/`DelayedTimeUTC_RFC3339`, `Timezone`, `Count`, `Complete`, `Success`, `Failed`, `Price`, `Recipients`, `TotalRecords`/`RecordsPerPage`/`PageCount`/`Page`, `ErrorMessage`.
- `Reschedule(...)`/`Abort(...)`/`Resubmit(...)` → `EmailActionResult`: `Result`, `ActionResult`, `MessageID`, `JobNum`, `Status`, `Action`, `ErrorMessage`.

`EmailResponse`/`EmailStatus`/`EmailActionResult` were named `...DTO` before this SDK's public response types dropped that internal-architecture suffix; the old names still work (they emit a `DeprecationWarning`) — see [messaging.md](messaging.md#response-shape).

### Recipient dict (each entry in `Status(...)`'s `Recipients`)

Unlike SMS, Email's `Recipients` entries are plain `dict`s, not typed objects — access fields with
`recipient["Field"]`/`recipient.get("Field")`, not attribute access.

| Key | Description |
|---|---|
| `Type` | Recipient channel type. |
| `DestSeq` | TNZ's internal sequence ID for this recipient within the job. |
| `Destination` | The recipient's email address. |
| `ContactID` | Addressbook contact reference, if sent via `ContactID`/`GroupID`. |
| `Status` | Delivery status for this recipient. |
| `Result` | Human-readable delivery result for this recipient. |
| `SentTimeLocal` / `SentTimeUTC` / `SentTimeUTC_RFC3339` | When the message was actually sent to this recipient. |
| `Attention` / `Company` / `Custom1`–`Custom9` | Echoed personalisation fields — see Destination fields above. |
| `RemoteID` | Carrier/network-assigned identifier for this delivery, if available. |
| `Price` | Per-recipient cost. |

## See also

- [README — Email](../README.md#email)
- [Samples — email_samples.py](../samples/messaging/email_samples.py)
