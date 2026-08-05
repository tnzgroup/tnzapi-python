# Messaging

Send messages across eight channels via `client.Messaging.<Channel>.SendMessage(...)`.

| Channel | Doc | Description |
|---|---|---|
| SMS | [sms.md](sms.md) | Text messages with optional fallback (e.g. Voice) |
| Email | [email.md](email.md) | Plain-text/HTML email with attachments |
| TTS | [tts.md](tts.md) | Text-to-speech voice calls with keypad routing |
| Voice | [voice.md](voice.md) | Pre-recorded audio calls with keypad routing |
| Fax | [fax.md](fax.md) | PDF/document fax with attachments |
| WhatsApp | [whatsapp.md](whatsapp.md) | WhatsApp template messages with fallback |
| RCS | [rcs.md](rcs.md) | Rich Communication Services messages |
| Workflow | [workflow.md](workflow.md) | Multi-channel Workflow Template triggers |

## Common parameters

Every channel's `<X>Request` shares most of these fields (see each channel's page for its full table and any channel-specific fields):

| Parameter | Type | Description |
|---|---|---|
| `Reference` | `str` | Your internal reference, returned in reports and webhooks. |
| `MessageID` | `str` | Supply your own message ID (otherwise auto-generated). |
| `SendTime` | `str` | Schedule delivery — combine with `Timezone`. |
| `Timezone` | `str` | Timezone name for `SendTime` (e.g. `"New Zealand"`, `"Pacific/Auckland"`). |
| `SubAccount` | `str` | Sub-account code for billing separation. |
| `Department` | `str` | Department code. |
| `WebhookCallbackURL` | `str` | URL for delivery status callbacks. |
| `WebhookCallbackFormat` | `str` | Callback format (`JSON`/`XML`/`POST`/`GET`). |
| `NotificationType` | `str` | Notification delivery mode. |
| `ReportTo` | `str` | Email address to receive delivery reports. |
| `Mode` | `str` | Set `"Test"` to validate without sending. Default `"Live"`. |

> `ReportTo` is supported by SMS, Email, Fax, TTS, and Voice — it is **not** available on WhatsApp, RCS, or Workflow.
> `Mode` is supported by every channel except Workflow, which has no "Test" send mode at all.

## Destinations

Every channel except Workflow addresses a single recipient type per destination entry (a phone number, an email address, etc. — see each channel's own "Destination fields" table for its exact keys). Workflow's destinations are the one exception: genuinely omni-channel, a single entry can carry `ToNumber`, `MainPhone`, and `EmailAddress` all at once, letting the Workflow Template decide which channel(s) actually get used — see [workflow.md](workflow.md).

A destination can always be set one of four ways:
- A single shorthand string via the `Destination`/`ToNumber`/`EmailAddress` (channel-dependent) kwarg.
- A list of dicts via the `Destinations` kwarg — each dict's keys are documented per channel. A bare string is also accepted as a list item (e.g. `Destinations=["+64211111111"]`) and is normalized identically to `AddDestination(...)`'s own shorthand handling — `Set(Destinations=["+64211111111"])` and `AddDestination("+64211111111")` always produce the same result.
- A single `ContactID`/`GroupID` kwarg, resolved against your Addressbook.
- Chained `AddDestination(...)` calls on the builder — accepts a string, a dict, a list of either, or `ContactID=`/`GroupID=` keyword form.

Every destination dict (or `Destination` instance) is validated against
`tnzapi.core.destination.Destination`'s known fields (`Recipient`, `ToNumber`, `MobilePhone`,
`MainPhone`, `FaxNumber`, `EmailAddress`, `ContactID`, `GroupID`, `GroupCode`, `Attention`,
`FirstName`, `LastName`, `Company`, `Custom1`-`Custom9`) — an unknown key raises `ValueError`
(`Set()`/`AddDestination()`) or returns `Result="Failed"` (`SendMessage()`), matching this SDK's
existing unknown-top-level-field behavior. See `tnzapi.core.destination.Destination` to construct
one directly instead of a raw dict.

## Builder pattern

Every channel supports a fluent `Set(**kwargs)` builder as an alternative to passing every field to `SendMessage(**kwargs)` directly:

```python
response = (
    client.Messaging.SMS
    .Set(
        Message="Test SMS",
        Reference="Test SMS - Builder sample"
    )
    .AddDestination("+64211111111")
    .AddDestination("+64222222222")
    .SendMessage()
)
```

TTS and Voice additionally support `.AddKeypad(...)`. Email, Fax, RCS, SMS, and WhatsApp additionally support `.AddAttachment(Name, Data)`.

`Set(**kwargs)` raises `ValueError` on an unknown field name — this is the one place in this pattern that raises, since a chainable builder method can't return a Result DTO on failure. `SendMessage(**kwargs)`/`SendMessage(model=...)`, by contrast, return `Result="Failed"` on an unknown field rather than raising.

## Response shape

Every `SendMessage(...)` call returns a dataclass with at least `Result`, `MessageID`, and `ErrorMessage`:

```python
if response.Result == "Success":
    print(f"Success - MessageID: {response.MessageID}")
else:
    for error in response.ErrorMessage:
        print(f"- Error={error}")
```

`Result` is one of four string values: `"Success"`, `"Failed"`, `"Unauthorized"`, `"RecordNotFound"`. See each channel's page for the extra fields its `Status`/`Received`/Action results carry.

Every response class listed on those pages (e.g. `SMSResponse`, `SMSStatus`) is also importable from `tnzapi.models` (e.g. `from tnzapi.models import SMSResponse`) — a shallow alternative to each channel's own deep `tnzapi.api.v300....models.responses...` import path. These classes were named with a `...DTO` suffix in earlier versions; the old names still work but emit a `DeprecationWarning`.

## Authentication

```python
from tnzapi import TNZAPI

client = TNZAPI(AuthToken="[Your Auth Token]")
```

See [README — Configuration](../README.md#configuration) for details, including environment-variable-based configuration.
