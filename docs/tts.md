# TTS (Text-to-Speech)

Place automated text-to-speech voice calls, with optional keypad-menu routing, via the TNZ REST API.

→ [Common parameters & authentication](../README.md#messaging)

## Quick example

```python
from tnzapi import TNZAPI

client = TNZAPI(AuthToken="[Your Auth Token]")

response = client.Messaging.TTS.SendMessage(
    MessageToPeople="Hi there!",
    Destination="+64211232345",
    Reference="Voice Test - 64211232345"
)

if response.Result == "Success":
    print(f"Success - MessageID: {response.MessageID}")
```

## Parameters (`TTSRequest`)

**Unlike Voice's same-named fields**, TTS's `MessageToPeople`/`MessageToAnswerPhones`/
`CallRouteMessageOnWrongKey`/`CallRouteMessageToPeople`/`CallRouteMessageToOperators`/`AddKeypad(...,
Play=...)` are plain spoken text, synthesized at send time — never base64 audio, never file-path-detected.
Passing an existing file's path as `MessageToPeople` here stores it as literal text to be read aloud, not a
reference to that file's contents. See [docs/voice.md](voice.md) for the audio-file-based equivalents.

| Parameter | Type | Required | Description |
|---|---|---|---|
| `MessageToPeople` | `str` | Yes* | Text read aloud to a human answering the call. |
| `TemplateID` | `str` | Yes* | Pre-configured message template ID (alternative to `MessageToPeople`). |
| `Destination` | `str` | Yes† | Single destination shorthand, e.g. `"+64211111111"`. |
| `ToNumber` | `str` | Yes† | Alternative single-destination field. |
| `Destinations` | `list[dict]` | Yes† | One or more destinations — see Destination fields below. |
| `ContactID` | `str` | No | Single addressbook contact to send to (alternative/addition to `Destinations`). |
| `GroupID` | `str` | No | Single addressbook group to send to (alternative/addition to `Destinations`). |
| `MessageID` | `str` | No | Supply your own message ID (otherwise auto-generated). |
| `Reference` | `str` | No | Your internal reference, returned in reports and webhooks. |
| `MessageToAnswerPhones` | `str` | No | Alternative text read when an answering machine picks up. |
| `AnswerPhoneMode` | `str` | No | How to handle an answering machine. |
| `Keypads` | `list[dict]` | No | Keypad menu options — see Keypad fields below. |
| `KeypadOptionRequired` | `bool` | No | Force the caller to press a key before the call proceeds. Default `False`. |
| `CallRouteMessageOnWrongKey` | `str` | No | Message played if an invalid key is pressed. |
| `CallRouteMessageToPeople` | `str` | No | Message played before routing to an operator. |
| `CallRouteMessageToOperators` | `str` | No | Message played to the operator receiving the routed call. |
| `NumberOfOperators` | `int` | No | Number of simultaneous operators for keypad-routed calls. Also settable in-flight via `Pacing(...)`. |
| `RetryAttempts` | `int` | No | Number of retry attempts on no-answer/busy. |
| `RetryPeriod` | `int` | No | Minutes between retry attempts. |
| `CallerID` | `str` | No | Caller ID shown to the recipient. |
| `Voice` | `str` | No | TTS voice to use. |
| `Options` | `str` | No | Additional provider-specific options. |
| `NotificationType` | `str` | No | Notification delivery mode. |
| `WebhookCallbackURL` | `str` | No | URL for delivery status callbacks. |
| `WebhookCallbackFormat` | `str` | No | Callback format (`JSON`/`XML`/`POST`/`GET`). |
| `ReportTo` | `str` | No | Email address to receive delivery reports. |
| `SendTime` | `str` | No | Schedule delivery — combine with `Timezone`. |
| `Timezone` | `str` | No | Timezone name for `SendTime` (e.g. `"New Zealand"`, `"Pacific/Auckland"`). |
| `SubAccount` | `str` | No | Sub-account code for billing separation. |
| `Department` | `str` | No | Department code. |
| `Mode` | `str` | No | Set `"Test"` to validate without sending. Default `"Live"`. Also accepts the typed `SendMode` enum (`SendMode.Test`/`SendMode.Live`) - see [Send Mode reference](../README.md#send-mode-reference). |

\*Either `MessageToPeople` or `TemplateID` must be provided.
†Set via `Destination`/`ToNumber`/`Destinations`, or via `AddDestination(...)` on the builder.

## Keypad fields (`Keypads` list items)

Built via `AddKeypad(Tone, Play=None, RouteNumber=None, PlaySection=None)` on the builder, or supplied directly as dicts in `Keypads`. `AddKeypads([...])` adds several keypad entries in one call - each item is a plain dict of the same fields, e.g. `AddKeypads([{"Tone": 1, "RouteNumber": "+6491234567"}, {"Tone": 2, "Play": "You pressed 2"}])`.

| Field | Description |
|---|---|
| `Tone` | The DTMF digit this entry responds to. |
| `Play` | Message played when this key is pressed. |
| `RouteNumber` | Phone number to route the call to when this key is pressed. |
| `PlaySection` | Which section of the call this keypad entry applies to: `"Main"` (the main `MessageToPeople`), `"AnswerPhone"` (simulates answering-machine pickup, plays `MessageToAnswerPhones`), or `"WrongKey"` (plays `CallRouteMessageOnWrongKey`). |

## Destination fields (`Destinations` list items)

| Field | Description |
|---|---|
| `ToNumber` | Destination phone number, e.g. `"+64211111111"`. |
| `Recipient` | Generic destination address, sent as-is regardless of channel — same effect as `ToNumber` here. |
| `MainPhone` | Alternative phone field, same effect as `ToNumber` for this channel. |
| `MobilePhone` | Accepted but not read by TTS (used by SMS/WhatsApp/RCS). |
| `EmailAddress` | Accepted but not read by TTS (used by Email). |
| `FaxNumber` | Accepted but not read by TTS (used by Fax). |
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
response = client.Messaging.TTS.SendMessage(
    MessageToPeople="Hi there!",
    Destinations=[{"ToNumber": "+64211232345"}],
    Reference="Voice Test - 64211232345",
    Keypads=[{"Tone": 1, "Play": "You pressed 1", "RouteNumber": "+6491232345"}]
)
```

### Builder with a keypad menu

```python
response = (
    client.Messaging.TTS
    .Set(
        MessageToPeople="Hi there!",
        Reference="Voice Test - 64211232345",
    )
    .AddDestination("+64211232345")
    .AddKeypad(
        Tone=1,
        Play="You pressed 1",
        RouteNumber="+6491232345",
    )
    .SendMessage()
)
```

### Keypad menu, via `AddKeypads`

`AddKeypads([...])` adds several keypad entries in one call - each item is a plain dict of the same
fields `AddKeypad(...)` takes.

```python
response = (
    client.Messaging.TTS
    .Set(
        MessageToPeople="Press 1 for sales, press 2 for support.",
        Reference="Voice Test - 64211232345",
    )
    .AddDestination("+64211232345")
    .AddKeypads([
        {"Tone": 1, "RouteNumber": "+6491001001"},
        {"Tone": 2, "RouteNumber": "+6491001002"},
    ])
    .SendMessage()
)
```

### Multiple destinations

```python
response = (
    client.Messaging.TTS
    .Set(
        MessageToPeople="Hi there!"
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
    client.Messaging.TTS
    .Set(MessageToPeople="Hi there!")
    .AddDestinations(["+64211232345", "+64211232346"])
    .SendMessage()
)
```

### Addressbook destination

```python
response = (
    client.Messaging.TTS
    .Set(
        MessageToPeople="Hi there!"
    )
    .AddDestination(ContactID="[Contact ID]")
    .AddDestination(GroupID="[Group ID]")
    .SendMessage()
)
```

### With personalisation, via typed `Destination`

```python
from tnzapi.core.destination import Destination

response = (
    client.Messaging.TTS
    .Set(
        MessageToPeople="Hi [[FirstName]], your appointment is on [[Custom1]]."
    )
    .AddDestinations([
        Destination(
            MainPhone="+64211232345",
            FirstName="Alice",
            Custom1="Monday 3pm",
        ),
        Destination(
            MainPhone="+64211232346",
            FirstName="Bob",
            Custom1="Tuesday 10am",
        ),
    ])
    .SendMessage()
)
```

### Retry attempts, caller ID, and reporting

```python
response = client.Messaging.TTS.SendMessage(
    MessageToPeople="Hi there!",
    Destination="+64211232345",
    RetryAttempts=3,
    RetryPeriod=15,
    CallerID="+6491000000",
    Voice="Female",
    ReportTo="reports@example.com",
)
```

### Multi-option IVR menu with wrong-key handling

```python
response = (
    client.Messaging.TTS
    .Set(
        MessageToPeople="Press 1 for sales, press 2 for support.",
        Reference="IVR Test - 64211232345",
        KeypadOptionRequired=True,
        CallRouteMessageOnWrongKey="Sorry, that wasn't a valid option.",
        CallRouteMessageToPeople="Please hold while we transfer your call.",
        CallRouteMessageToOperators="Incoming call from the IVR menu.",
        NumberOfOperators=2,
    )
    .AddDestination("+64211232345")
    .AddKeypad(
        Tone=1,
        Play="Transferring you to sales.",
        RouteNumber="+6491001001",
    )
    .AddKeypad(
        Tone=2,
        Play="Transferring you to support.",
        RouteNumber="+6491001002",
    )
    .AddKeypad(
        Tone=3,
        Play="Here are our opening hours.",
    )
    .AddKeypad(
        Tone=9,
        PlaySection="Main",
    )
    .SendMessage()
)
```

`Tone=3` above plays a message with no `RouteNumber` at all — a keypad entry doesn't have to route the
call anywhere, it can just play something. `Tone=9` uses `PlaySection="Main"` to let the caller replay
the original `MessageToPeople` — a keypad entry doesn't have to reference `Play`/`RouteNumber` either.

### Scheduled send

```python
response = client.Messaging.TTS.SendMessage(
    MessageToPeople="Hi there!",
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
    client.Messaging.TTS
    .Set(
        MessageToPeople="Hi there!",
        Mode=SendMode.Test
    )
    .AddDestination("+64211232345")
    .SendMessage()
)
```

### Poll for status

```python
status = client.Messaging.TTS.Status(MessageID=response.MessageID)

if status.Result == "Success":
    print(f"JobStatus: {status.JobStatus}")
    for recipient in status.Recipients:
        print(f" -> {recipient}")
```

### Reschedule / Abort / Resubmit

```python
client.Messaging.TTS.Reschedule(
    MessageID=response.MessageID,
    SendTime="2026-08-01T09:00:00",
)
client.Messaging.TTS.Abort(MessageID=response.MessageID)
client.Messaging.TTS.Resubmit(
    MessageID=response.MessageID,
    SendTime="2026-08-01T09:00:00",
)
```

### Pacing (adjust simultaneous operators)

```python
client.Messaging.TTS.Pacing(
    MessageID=response.MessageID,
    NumberOfOperators=10,
)
```

## Response

- `SendMessage(...)` → `TTSResponse`: `Result`, `MessageID`, `ErrorMessage`.
- `Status(...)` → `TTSStatus`: `Result`, `MessageID`, `JobStatus`, `JobNum`, `Account`, `SubAccount`, `Department`, `Reference`, `CreatedTimeLocal`/`CreatedTimeUTC`/`CreatedTimeUTC_RFC3339`, `DelayedTimeLocal`/`DelayedTimeUTC`/`DelayedTimeUTC_RFC3339`, `Timezone`, `Count`, `Complete`, `Success`, `Failed`, `Price`, `Recipients`, `TotalRecords`/`RecordsPerPage`/`PageCount`/`Page`, `ErrorMessage`.
- `Reschedule(...)`/`Abort(...)`/`Resubmit(...)`/`Pacing(...)` → `TTSActionResult`: `Result`, `ActionResult`, `MessageID`, `JobNum`, `Status`, `Action`, `ErrorMessage`.

`TTSResponse`/`TTSStatus`/`TTSActionResult` were named `...DTO` before this SDK's public response types dropped that internal-architecture suffix; the old names still work (they emit a `DeprecationWarning`) — see [messaging.md](messaging.md#response-shape).

### Recipient dict (each entry in `Status(...)`'s `Recipients`)

TTS's `Recipients` entries are plain `dict`s, not typed objects — access fields with
`recipient["Field"]`/`recipient.get("Field")`, not attribute access. **TTS calls report as
`Type: "Voice"`, not `"TTS"`** — keep this in mind if you're filtering `recipient["Type"]`.

| Key | Description |
|---|---|
| `Type` | Recipient channel type — `"Voice"` for TTS calls (see note above). |
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

- [README — TTS](../README.md#tts)
- [Samples — tts_samples.py](../samples/messaging/tts_samples.py)
