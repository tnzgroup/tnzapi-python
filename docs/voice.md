# Voice

Place automated pre-recorded-audio calls, with optional keypad-menu routing, via the TNZ REST API.

→ [Common parameters & authentication](../README.md#messaging)

## Quick example

```python
from tnzapi import TNZAPI

client = TNZAPI(AuthToken="[Your Auth Token]")

response = client.Messaging.Voice.SendMessage(
    MessageToPeople="path/to/audio.wav",
    Destination="+64211232345",
    Reference="Voice Test - 64211232345"
)

if response.Result == "Success":
    print(f"Success - MessageID: {response.MessageID}")
```

## Parameters (`VoiceRequest`)

`MessageToPeople`, `MessageToAnswerPhones`, `CallRouteMessageOnWrongKey`, `CallRouteMessageToPeople`,
`CallRouteMessageToOperators`, and `AddKeypad(..., Play=...)` all accept a local file path directly (the
file is read and base64-encoded automatically), a `tnzapi.core.file_attachment.FileAttachment` instance
(`.Data` is used, `.Name` is ignored — these fields have no filename concept), or a pre-encoded base64
string, passed through unchanged. **Unlike TTS's same-named fields** (plain spoken text, see
[docs/tts.md](tts.md)), these are always audio.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `MessageToPeople` | `str` | Yes* | Base64-encoded wav/mp3 audio played to a person answering the call. |
| `TemplateID` | `str` | Yes* | Pre-configured audio template ID (alternative to `MessageToPeople`). |
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
| `MessageToAnswerPhones` | `str` | No | Base64-encoded wav/mp3 audio played if an answering machine picks up instead of a person. |
| `AnswerPhoneMode` | `str` | No | How to handle an answering machine (e.g. play `MessageToAnswerPhones`, hang up, etc). |
| `Keypads` | `list[dict]` | No | Keypad menu options built via `AddKeypad(...)` — see Keypad fields below. |
| `KeypadOptionRequired` | `bool` | No | Force the recipient to press a key before the call proceeds. Default `False`. |
| `CallRouteMessageOnWrongKey` | `str` | No | Base64-encoded audio played if an invalid key is pressed. |
| `CallRouteMessageToPeople` | `str` | No | Base64-encoded audio played before routing the call to an operator. |
| `CallRouteMessageToOperators` | `str` | No | Base64-encoded audio played to the operator receiving the routed call. |
| `NumberOfOperators` | `int` | No | Number of simultaneous operators for keypad-routed calls. Also settable in-flight via `Pacing(...)`. |
| `RetryAttempts` | `int` | No | Number of retry attempts on no-answer/busy. |
| `RetryPeriod` | `int` | No | Minutes between retry attempts. |
| `CallerID` | `str` | No | Caller ID shown to the recipient. |
| `Options` | `str` | No | Additional provider-specific options. |
| `Mode` | `str` | No | Set `"Test"` to validate without sending. Default `"Live"`. Also accepts the typed `SendMode` enum (`SendMode.Test`/`SendMode.Live`) - see [Send Mode reference](../README.md#send-mode-reference). |

\*Either `MessageToPeople` or `TemplateID` must be provided — unlike TTS/SMS/Email, Voice's primary content field is genuinely optional at the field-definition level when a `TemplateID` supplies the pre-recorded audio instead.
†Set via `Destination`/`ToNumber`/`Destinations`, or via `AddDestination(...)` on the builder.

Voice has no separate `Voice` field the way TTS does — its wire body carries only `MessageToPeople`/`MessageToAnswerPhones` (both pre-recorded audio), never text-to-speech text.

## Keypad fields (`Keypads` list items)

Built via `AddKeypad(Tone, Play=None, RouteNumber=None, PlaySection=None)` on the builder, or supplied directly as dicts in `Keypads`. `AddKeypads([...])` adds several keypad entries in one call - each item is a plain dict of the same fields, e.g. `AddKeypads([{"Tone": 1, "RouteNumber": "+6491234567"}, {"Tone": 2, "Play": "You pressed 2"}])`.

| Field | Description |
|---|---|
| `Tone` | The keypad digit this entry matches (`int`, e.g. `1`). |
| `Play` | Optional base64-encoded audio played when this key is pressed, before routing. |
| `RouteNumber` | Phone number to route the call to when this key is pressed. |
| `PlaySection` | Which section of the call this keypad entry applies to: `"Main"` (the main `MessageToPeople`), `"AnswerPhone"` (simulates answering-machine pickup, plays `MessageToAnswerPhones`), or `"WrongKey"` (plays `CallRouteMessageOnWrongKey`). |

## Destination fields (`Destinations` list items)

| Field | Description |
|---|---|
| `ToNumber` | Destination phone number, e.g. `"+64211111111"`. |
| `Recipient` | Generic destination address, sent as-is regardless of channel — same effect as `ToNumber` here. |
| `MainPhone` | Alternative phone field, same effect as `ToNumber` for this channel. |
| `MobilePhone` | Accepted but not read by Voice (used by SMS/WhatsApp/RCS). |
| `EmailAddress` | Accepted but not read by Voice (used by Email). |
| `FaxNumber` | Accepted but not read by Voice (used by Fax). |
| `ContactID` | Addressbook contact reference — sends to that contact instead of a raw number. |
| `GroupID` | Addressbook group reference — sends to all members of that group. |
| `GroupCode` | Alternative group lookup by code (instead of `GroupID`). |
| `FirstName` / `LastName` / `Company` / `Attention` | Personalisation tokens, e.g. `[[FirstName]]`. |
| `Custom1`–`Custom9` | Arbitrary per-recipient personalisation values, `[[Custom1]]` … `[[Custom9]]`. |

A `tnzapi.core.destination.Destination` instance can be used instead of a raw dict — it validates
field names at construction time (`Destination(ToNumber="...", Bogus="...")` raises `TypeError`),
and an unknown key in a raw dict is now rejected the same way (`ValueError` for `Set()`/
`AddDestination()`, `Result="Failed"` for `SendMessage()`).

## Code samples

### Flat kwargs

```python
response = client.Messaging.Voice.SendMessage(
    MessageToPeople="path/to/audio.wav",
    MessageToAnswerPhones="path/to/audio.wav",
    Destinations=[{"ToNumber": "+64211232345"}],
    Reference="Voice Test - 64211232345",
    Keypads=[{"Tone": 1, "RouteNumber": "+6491232345"}]
)
```

### Builder

```python
response = (
    client.Messaging.Voice
    .Set(
        MessageToPeople="path/to/audio.wav",
        Reference="Voice Test - 64211232345",
    )
    .AddDestination("+64211232345")
    .AddKeypad(Tone=1, RouteNumber="+6491232345")
    .SendMessage()
)
```

### From a file path

A local audio file path is read and base64-encoded automatically — no manual `base64` handling needed:

```python
response = (
    client.Messaging.Voice
    .Set(
        MessageToPeople = "path/to/audio.wav",
    )
    .AddDestination("+64211232345")
    .SendMessage()
)
```

### Using the typed `FileAttachment`

```python
from tnzapi.core.file_attachment import FileAttachment

response = (
    client.Messaging.Voice
    .Set(
        MessageToPeople = FileAttachment("path/to/audio.wav"),
    )
    .AddDestination("+64211232345")
    .SendMessage()
)
```

### Multiple destinations

```python
response = (
    client.Messaging.Voice
    .Set(
        MessageToPeople="path/to/audio.wav"
    )
    .AddDestination("+64211232345")
    .AddDestination("+64211232346")
    .SendMessage()
)
```

### Multiple destinations, via `AddDestinations`

`AddDestinations([...])` adds several destinations in one call on the builder - each item can be a bare
string, a dict, or a typed `Destination`, mixed freely in the same list. Unlike `AddDestination(...)`
(singular), which only ever adds one destination per call and raises `TypeError` on a list, this is the
chainable way to add several at once.

```python
response = (
    client.Messaging.Voice
    .Set(MessageToPeople="path/to/audio.wav")
    .AddDestinations(["+64211232345", "+64211232346"])
    .SendMessage()
)
```

### Addressbook destination

```python
response = (
    client.Messaging.Voice
    .Set(
        MessageToPeople="path/to/audio.wav"
    )
    .AddDestination(ContactID="[Contact ID]")
    .AddDestination(GroupID="[Group ID]")
    .SendMessage()
)
```

### With personalisation, via typed `Destination`

Personalisation fields can't be spoken by pre-recorded audio, but they're still accepted on the
destination and echoed back in status reports.

```python
from tnzapi.core.destination import Destination

response = (
    client.Messaging.Voice
    .Set(
        MessageToPeople="path/to/audio.wav"
    )
    .AddDestinations([
        Destination(
            MainPhone="+64211232345",
            FirstName="Alice",
            Custom1="Account #4432",
        ),
        Destination(
            MainPhone="+64211232346",
            FirstName="Bob",
            Custom1="Account #7788",
        ),
    ])
    .SendMessage()
)
```

### Retry attempts, caller ID, and billing codes

```python
response = client.Messaging.Voice.SendMessage(
    MessageToPeople="path/to/audio.wav",
    Destination="+64211232345",
    RetryAttempts=3,
    RetryPeriod=5,
    CallerID="+6491000000",
    SubAccount="Sales",
    Department="Outbound",
    ReportTo="reports@example.com",
)
```

### IVR menu with keypad routing

```python
response = (
    client.Messaging.Voice
    .Set(
        MessageToPeople="path/to/press-1-for-sales-2-for-support.wav",
        Reference="IVR Test - 64211232345",
        KeypadOptionRequired=True,
        CallRouteMessageOnWrongKey="path/to/invalid-option.wav",
        CallRouteMessageToPeople="path/to/please-hold.wav",
        CallRouteMessageToOperators="path/to/incoming-ivr-call.wav",
        NumberOfOperators=2,
    )
    .AddDestination("+64211232345")
    .AddKeypad(Tone=1, RouteNumber="+6491001001")
    .AddKeypad(Tone=2, RouteNumber="+6491001002")
    .AddKeypad(Tone=3, Play="path/to/opening-hours.wav")
    .AddKeypad(Tone=9, PlaySection="Main")
    .SendMessage()
)
```

`Tone=3` above plays audio with no `RouteNumber` at all — a keypad entry doesn't have to route the call
anywhere, it can just play something. `Tone=9` uses `PlaySection="Main"` to let the caller replay the
original `MessageToPeople` — a keypad entry doesn't have to reference `Play`/`RouteNumber` either.

### Keypad menu, via `AddKeypads`

`AddKeypads([...])` adds several keypad entries in one call - each item is a plain dict of the same
fields `AddKeypad(...)` takes.

```python
response = (
    client.Messaging.Voice
    .Set(
        MessageToPeople="path/to/press-1-for-sales-2-for-support.wav",
        Reference="IVR Test - 64211232345",
    )
    .AddDestination("+64211232345")
    .AddKeypads([
        {"Tone": 1, "RouteNumber": "+6491001001"},
        {"Tone": 2, "RouteNumber": "+6491001002"},
    ])
    .SendMessage()
)
```

### Scheduled send

```python
response = client.Messaging.Voice.SendMessage(
    MessageToPeople="path/to/audio.wav",
    Destination="+64211232345",
    SendTime="2026-08-01T09:00:00",
    Timezone="Pacific/Auckland"
)
```

### Test mode (validate without sending)

`Mode` also accepts the typed `SendMode` enum as an equivalent alternative to the plain string -
`Mode=SendMode.Test` and `Mode="Test"` are fully interchangeable:

```python
from tnzapi.core.send_mode import SendMode

response = (
    client.Messaging.Voice
    .Set(
        MessageToPeople="path/to/audio.wav",
        Mode=SendMode.Test
    )
    .AddDestination("+64211232345")
    .SendMessage()
)
```

### Poll for status

```python
status = client.Messaging.Voice.Status(MessageID=response.MessageID)

if status.Result == "Success":
    print(f"JobStatus: {status.JobStatus}")
    for recipient in status.Recipients:
        print(f" -> {recipient}")
```

### Reschedule / Abort / Resubmit

```python
client.Messaging.Voice.Reschedule(
    MessageID=response.MessageID,
    SendTime="2026-08-01T09:00:00",
)
client.Messaging.Voice.Abort(MessageID=response.MessageID)
client.Messaging.Voice.Resubmit(
    MessageID=response.MessageID,
    SendTime="2026-08-01T09:00:00",
)
```

### Pacing

Adjust the number of operators for an in-flight keypad-routed job:

```python
client.Messaging.Voice.Pacing(
    MessageID=response.MessageID,
    NumberOfOperators=10,
)
```

## Response

- `SendMessage(...)` → `VoiceResponse`: `Result`, `MessageID`, `ErrorMessage`.
- `Status(...)` → `VoiceStatus`: `Result`, `MessageID`, `JobStatus`, `JobNum`, `Account`, `SubAccount`, `Department`, `Reference`, `CreatedTimeLocal`/`CreatedTimeUTC`/`CreatedTimeUTC_RFC3339`, `DelayedTimeLocal`/`DelayedTimeUTC`/`DelayedTimeUTC_RFC3339`, `Timezone`, `Count`, `Complete`, `Success`, `Failed`, `Price`, `Recipients`, `TotalRecords`/`RecordsPerPage`/`PageCount`/`Page`, `ErrorMessage`.
- `Reschedule(...)`/`Abort(...)`/`Resubmit(...)`/`Pacing(...)` → `VoiceActionResult`: `Result`, `ActionResult`, `MessageID`, `JobNum`, `Status`, `Action`, `ErrorMessage`. All four action methods share this one response type.

`VoiceResponse`/`VoiceStatus`/`VoiceActionResult` were named `...DTO` before this SDK's public response types dropped that internal-architecture suffix; the old names still work (they emit a `DeprecationWarning`) — see [messaging.md](messaging.md#response-shape).

### Recipient dict (each entry in `Status(...)`'s `Recipients`)

Voice's `Recipients` entries are plain `dict`s, not typed objects — access fields with
`recipient["Field"]`/`recipient.get("Field")`, not attribute access.

| Key | Description |
|---|---|
| `Type` | Recipient channel type — `"Voice"`. |
| `DestSeq` | TNZ's internal sequence ID for this recipient within the job. |
| `Destination` | The recipient's phone number. |
| `ContactID` | Addressbook contact reference, if sent via `ContactID`/`GroupID`. |
| `Status` | Delivery status for this recipient. |
| `Result` | Human-readable delivery result for this recipient. |
| `SentTimeLocal` / `SentTimeUTC` / `SentTimeUTC_RFC3339` | When the call was actually placed to this recipient. |
| `Attention` / `Company` / `Custom1`–`Custom9` | Echoed personalisation fields — see Destination fields above. |
| `RemoteID` | Carrier/network-assigned identifier for this delivery, if available. |
| `Price` | Per-recipient cost. |

## See also

- [README — Voice](../README.md#voice)
- [Samples — voice_samples.py](../samples/messaging/voice_samples.py)
