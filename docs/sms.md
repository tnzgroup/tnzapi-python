# SMS

Send text messages to one or more recipients via the TNZ REST API, with optional Voice/RCS/WhatsApp fallback.
SMS supports two-way messaging: track delivery status in real time (see "Poll for status" below), and receive
replies from recipients (see "Poll for inbound SMS" below, or webhooks for a push-based alternative).

→ [Common parameters & authentication](../README.md#messaging)

## Message body tokens

Beyond the personalisation tokens in the Destination fields table below, your `Message` body supports these
special inline tokens:

- `[[Link:https://example.com/page]]` — automatically shortens the URL and tracks click-through engagement.
- `[[File1]]` — inserts a link to the first file attached via `AddAttachment(...)`/`Files` (`[[File2]]`,
  `[[File3]]`, etc. for additional attachments).
- `[[REPLY]]` — inserts a tappable link recipients can use to reply, even from devices without native SMS
  reply support.
- `[[STOP]]` — inserts an unsubscribe link that automatically opts the recipient out of future messages.

## Quick example

```python
from tnzapi import TNZAPI

client = TNZAPI(AuthToken="[Your Auth Token]")

response = client.Messaging.SMS.SendMessage(
    Message="Test SMS Message click [[Reply]] to opt out",
    Destination="+64211231234",
    Reference="Test"
)

if response.Result == "Success":
    print(f"Success - MessageID: {response.MessageID}")
```

## Parameters (`SMSRequest`)

| Parameter | Type | Required | Description |
|---|---|---|---|
| `Message` | `str` | Yes* | Message body. Supports personalisation tokens `[[FirstName]]`, `[[Custom1]]`, etc. |
| `TemplateID` | `str` | Yes* | Pre-configured message template ID (alternative to `Message`). |
| `Destination` | `str` | Yes† | Single destination shorthand, e.g. `"+64211111111"`. |
| `ToNumber` | `str` | Yes† | Alternative single-destination field. |
| `Destinations` | `list[dict]` | Yes† | One or more destinations — see Destination fields below. |
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
| `FromNumber` | `str` | No | Sender ID shown on the recipient's device. |
| `SMSEmailReply` | `str` | No | Email address to receive SMS replies. |
| `CharacterConversion` | `bool` | No | Convert characters outside the GSM character set automatically. Default `False`. |
| `FallbackMode` | `str \| list[str]` | No | Fallback channel(s) if SMS fails, tried in the order given, e.g. `"Voice"` or `["Voice", "WhatsApp"]`. A list is joined into TNZ's wire format automatically (`"Voice, WAPP"`) - `"WhatsApp"` is translated to its real wire token `"WAPP"` either way. |
| `SMSCustomPageID` | `str` | No | Custom landing page ID for `[[Reply]]` links. |
| `Files` | `list[dict]` | No | MMS attachments — see `AddAttachment(Name, Data)` below. |
| `Mode` | `str` | No | Accepted values: `"Test"` — validates without sending. Omit for standard (live) sending. Also accepts the typed `SendMode` enum (`SendMode.Test`/`SendMode.Live`) - see [Send Mode reference](../README.md#send-mode-reference). |

\*Either `Message` or `TemplateID` must be provided.
†Set via `Destination`/`ToNumber`/`Destinations`, or via `AddDestination(...)` on the builder.

## Destination fields (`Destinations` list items)

| Field | Description |
|---|---|
| `ToNumber` | Destination phone number, e.g. `"+64211111111"`. |
| `Recipient` | Generic destination address, sent as-is regardless of channel — same effect as `ToNumber` here. |
| `MobilePhone` | Alternative phone field, same effect as `ToNumber` for this channel. |
| `MainPhone` | Accepted but not read by SMS (used by TTS/Voice). |
| `EmailAddress` | Accepted but not read by SMS (used by Email). |
| `FaxNumber` | Accepted but not read by SMS (used by Fax). |
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
response = client.Messaging.SMS.SendMessage(
    Message="Test SMS Message click [[Reply]] to opt out",
    Destination="+64211231234",
    Reference="Test"
)
```

### Builder

```python
response = (
    client.Messaging.SMS
    .Set(
        Message="Test SMS Message click [[Reply]] to opt out",
        Reference="Test"
    )
    .AddDestination("+64211231234")
    .SendMessage()
)
```

### Addressbook destination

```python
response = (
    client.Messaging.SMS
    .Set(Message="Hi [[FirstName]], see you soon!")
    .AddDestination(ContactID="[Contact ID]")
    .AddDestination(GroupID="[Group ID]")
    .SendMessage()
)
```

### Multiple recipients with personalisation

```python
response = client.Messaging.SMS.SendMessage(
    Message="Hi [[FirstName]]!",
    Destinations=[
        {"ToNumber": "+64211231234", "FirstName": "Alice"},
        {"ToNumber": "+64211231235", "FirstName": "Bob"},
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
    client.Messaging.SMS
    .Set(Message="Hi [[FirstName]]!")
    .AddDestinations([
        "+64211231234",
        {"ToNumber": "+64211231235", "FirstName": "Alice"},
    ])
    .SendMessage()
)
```

### Bulk send to multiple addressbook groups and contacts

Pass a list of `Destination` instances built from existing Addressbook groups and contacts directly to
the `Destinations` kwarg to message everyone in them in one call.

```python
from tnzapi.core.destination import Destination

response = client.Messaging.SMS.SendMessage(
    Message="Reminder: your subscription renews tomorrow.",
    Destinations=[
        Destination(GroupID="[Group ID 1]"),
        Destination(GroupID="[Group ID 2]"),
        Destination(ContactID="[Contact ID 1]"),
        Destination(ContactID="[Contact ID 2]"),
    ],
)
```

### Bulk send with per-destination personalisation, via typed `Destination`

```python
from tnzapi.core.destination import Destination

response = (
    client.Messaging.SMS
    .Set(
        Message="Hi [[FirstName]], your appointment is on [[Custom1]]."
    )
    .AddDestinations([
        Destination(
            ToNumber="+64211231234",
            FirstName="Alice",
            Custom1="Monday 3pm",
        ),
        Destination(
            ToNumber="+64211231235",
            FirstName="Bob",
            Custom1="Tuesday 10am",
        ),
    ])
    .SendMessage()
)
```

### Send a file via MessageLink

NZ carriers don't support MMS. Attach a file with `AddAttachment(...)` — a file path is read and
base64-encoded automatically — then reference it in the message text with `[[File1]]`; the recipient gets
an SMS with a link to the file instead of an inline attachment.

```python
response = (
    client.Messaging.SMS
    .Set(Message = "Here's the photo you requested: [[File1]]")
    .AddDestination("+64211231234")
    .AddAttachment("path/to/photo.jpg")
    .SendMessage()
)
```

### Multiple files, via `AddAttachments`

`AddAttachments([...])` adds several attachments in one call - each item can be a path string, a
`{"Name": ..., "Data": ...}` dict, or a `FileAttachment` instance, mixed freely in the same list.

```python
response = (
    client.Messaging.SMS
    .Set(Message="Here's what you requested: [[File1]] [[File2]]")
    .AddDestination("+64211231234")
    .AddAttachments(["path/to/photo.jpg", "path/to/receipt.pdf"])
    .SendMessage()
)
```

### Scheduled send with webhook callback

```python
response = client.Messaging.SMS.SendMessage(
    Message="Test SMS Message click [[Reply]] to opt out",
    Destination="+64211231234",
    SendTime="2026-08-01T09:00:00",
    Timezone="Pacific/Auckland",
    WebhookCallbackURL="https://example.com/webhooks/tnz/result",
    WebhookCallbackFormat="JSON",
)
```

### Test mode (validate without sending)

`Mode` also accepts the typed `SendMode` enum as an equivalent alternative to the plain string -
`Mode=SendMode.Test` and `Mode="Test"` are fully interchangeable:

```python
from tnzapi.core.send_mode import SendMode

response = (
    client.Messaging.SMS
    .Set(
        Message="Test SMS Message click [[Reply]] to opt out",
        Mode=SendMode.Test
    )
    .AddDestination("+64211231234")
    .SendMessage()
)
```

### Poll for status

```python
status = client.Messaging.SMS.Status(MessageID=response.MessageID)

if status.Result == "Success":
    print(f"JobStatus: {status.JobStatus}")
    for recipient in status.Recipients:
        print(f" -> {recipient}")
```

### Poll for replies

```python
replies = client.Messaging.SMS.Reply(response.MessageID)

if replies.Result == "Success":
    for recipient in replies.Recipients:
        for reply in recipient.SMSReplies:
            print(f"{recipient.Destination} replied: {reply.MessageText}")
```

### Poll for inbound SMS

```python
received = client.Messaging.SMS.Received(TimePeriod=1440)  # minutes

if received.Result == "Success":
    for message in received.Messages:
        print(message)
```

`Received(...)` only ever returns the requested page — it never auto-walks every page on your behalf. See `samples/messaging/_pagination.py`'s `WalkAllPages` helper if you need to walk everything.

### Reschedule / Abort

```python
client.Messaging.SMS.Reschedule(
    MessageID=response.MessageID,
    SendTime="2026-08-01T09:00:00",
)
client.Messaging.SMS.Abort(MessageID=response.MessageID)
```

SMS has no `Resubmit`/`Pacing` (those exist on Email/Fax/TTS/Voice — `Pacing` on TTS/Voice only).

## Response

- `SendMessage(...)` → `SMSResponse`: `Result`, `MessageID`, `ErrorMessage`.
- `Status(...)` → `SMSStatus`: `Result`, `MessageID`, `JobStatus`, `JobNum`, `Account`, `SubAccount`, `Department`, `Reference`, `CreatedTimeLocal`/`CreatedTimeUTC`/`CreatedTimeUTC_RFC3339`, `DelayedTimeLocal`/`DelayedTimeUTC`/`DelayedTimeUTC_RFC3339`, `Timezone`, `Count`, `Complete`, `Success`, `Failed`, `Price`, `Recipients`, `TotalRecords`/`RecordsPerPage`/`PageCount`/`Page`, `ErrorMessage`. Each `Recipients` item is a typed `SMSRecipient` (`Type`, `DestSeq`, `Destination`, `ContactID`, `Status`, `Result`, `MessageText`, `SentTimeLocal`/`SentTimeUTC`/`SentTimeUTC_RFC3339`, `Attention`, `Company`, `Custom1`-`Custom9`, `RemoteID`, `Price`, `SMSReplies`) supporting both attribute access (`recipient.Destination`) and dict-style access (`recipient['Destination']`, `recipient.get('SMSReplies', [])`) for backward compatibility. Each `SMSReplies` item is a typed `SMSReply` (`ReceivedID`, `ReceivedTimeLocal`/`ReceivedTimeUTC`/`ReceivedTimeUTC_RFC3339`, `Timezone`, `From`, `MessageText`), same dual access.
- `Reply(...)` → same `SMSStatus` as `Status(...)` — a more ergonomically-named alias for polling replies to a specific sent message, taking the same `MessageID`/`RecordsPerPage`/`Page` arguments.
- `Received(...)` → `SMSReceived`: `Result`, `Messages`, `TotalRecords`/`RecordsPerPage`/`PageCount`/`Page`, `ErrorMessage`.
- `Reschedule(...)`/`Abort(...)` → `SMSActionResult`: `Result`, `ActionResult`, `MessageID`, `JobNum`, `Status`, `Action`, `ErrorMessage`.

`SMSResponse`/`SMSStatus`/`SMSRecipient`/`SMSReply`/`SMSReceived`/`SMSActionResult` were named `...DTO` before this SDK's public response types dropped that internal-architecture suffix; the old names still work (they emit a `DeprecationWarning`) — see [messaging.md](messaging.md#response-shape).

### Recipient object (each entry in `Status(...)`'s `Recipients`)

SMS is the one channel where `Recipients` (and each recipient's nested `SMSReplies`) are real dataclass
instances rather than plain dicts — every other channel's `Recipients`/`Messages` stay plain `dict` lists.
Existing dict-style access still works unchanged (`recipient["Status"]`, `recipient.get("Status")`), and
attribute access (`recipient.Status`) works too, either style. A field the API returns that isn't in the
table below is preserved and still reachable via dict-style access; it just won't have a matching attribute.

| Field | Description |
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
| `SMSReplies` | Inbound replies from this recipient, same dict-plus-attribute access as `Recipients` above. See table below. |

### SMSReplies object (each entry in `Recipients[].SMSReplies`)

| Field | Description |
|---|---|
| `ReceivedID` | Unique identifier for this reply. |
| `ReceivedTimeLocal` / `ReceivedTimeUTC` / `ReceivedTimeUTC_RFC3339` | When the reply was received. |
| `Timezone` | Timezone name for `ReceivedTimeLocal`. |
| `From` | The replying phone number. |
| `MessageText` | The reply body. |

Inbound SMS replies to a specific message also surface via `client.Reports.SMSReply.Poll(MessageID=...)` — see the Reports facade.

## See also

- [README — SMS](../README.md#sms)
- [Samples — sms_samples.py](../samples/messaging/sms_samples.py)
