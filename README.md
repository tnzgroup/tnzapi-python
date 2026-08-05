# tnzapi

`tnzapi` is the official Python helper library for the [TNZ Group](https://www.tnz.co.nz) REST API — send SMS, Email, Fax, TTS (text-to-speech), Voice, WhatsApp, RCS and Workflow messages, manage opt-outs, retrieve delivery reports, amend in-flight jobs, and manage your address book, all through a small, consistent Python surface over the v3.00 JSON API.

## Documentation

The documentation for the TNZ API can be found [here][apidocs].

Full parameter reference for this library is under [docs/](docs/messaging.md) — one page per messaging channel plus [Addressbook](docs/addressbook.md), [Opt-Out Management](docs/optout.md), and [Webhooks](docs/webhooks.md), including every field, type, and destination shape not covered by this README's quick examples.

## Versions

`tnzapi` uses a modified version of [Semantic Versioning](https://semver.org) for all changes. [See this document](VERSIONS.md) for details. See [CHANGELOG.md](CHANGELOG.md) for what's changed release to release.

### Supported Python Versions

This library supports the following Python implementations:

* Python 3.9
* Python 3.10
* Python 3.11
* Python 3.12
* Python 3.13
* Python 3.14

## Installation

Install from PyPi using [pip](http://www.pip-installer.org/en/latest/), a
package manager for Python.

    pip install tnzapi

Don't have pip installed? Try installing it, by running this from the command
line:

    $ curl https://raw.github.com/pypa/pip/master/contrib/get-pip.py | python

    python setup.py install

You may need to run the above commands with `sudo`.

## Configuration

Every v3.00 facade (`Messaging`, `Reports`, `Actions`, `Addressbook`, `OptOut`) authenticates with a Bearer `AuthToken` — pass it directly to the `TNZAPI` constructor, or leave it out and set it via environment variable instead:

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)
```

| Environment variable | Purpose |
|---|---|
| `TNZ_AUTH_TOKEN` | Used when `AuthToken` isn't passed to the `TNZAPI` constructor. |
| `TNZ_API_URL` | Overrides the default API base URL (`https://api.tnz.co.nz/api/v3.00`) — useful for pointing at a local/staging server. |
| `TNZ_ALLOW_INSECURE_HTTP` | Set to `true` to allow a non-HTTPS `TNZ_API_URL` (local dev only). By default, any base URL that isn't `https://` is rejected so the Bearer token is never sent over plain HTTP. |

## Quick Start

```python
from tnzapi import TNZAPI

client = TNZAPI(
    AuthToken="[Your Auth Token]"
)

response = client.Messaging.SMS.SendMessage(
    Message="Test SMS Message click [[Reply]] to opt out",
    Destination="+64211231234",
    Reference="Test"
)

if response.Result == "Success":
    print(response.MessageID)
else:
    print(response.ErrorMessage)
```

## Messaging

> **Parameter naming:** every request-class method (`Status`, `Reschedule`, `Received`, `List`, etc.) takes PascalCase keyword arguments (`MessageID=`, `RecordsPerPage=`, ...), matching the field names used throughout this SDK's DTOs. The previous snake_case names (`message_id=`, `records_per_page=`, ...) still work and will keep working - they're translated internally with a `DeprecationWarning` - but new code should use the PascalCase form.

Every messaging channel supports two equivalent calling styles:

- **Flat kwargs** — pass every field to `SendMessage(...)` in one call.
- **Builder** — chain `Set(...)`/`AddDestination(...)`/`AddAttachment(...)` calls and finish with `SendMessage()` (no arguments). `Build()` returns the underlying request DTO without sending, if you want to inspect or reuse it.

### SMS

```python
# Flat kwargs
response = client.Messaging.SMS.SendMessage(
    Message="Test SMS Message click [[Reply]] to opt out",
    Destinations=[{"ToNumber": "+64211231234"}],
    Reference="Test"
)

# Builder
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

Poll for replies to a sent message:

```python
replies = client.Messaging.SMS.Reply(response.MessageID)

if replies.Result == "Success":
    for recipient in replies.Recipients:
        for reply in recipient.SMSReplies:
            print(f"{recipient.Destination} replied: {reply.MessageText}")
```

**Full reference:** [docs/sms.md](docs/sms.md)

### Email

```python
# Flat kwargs
response = client.Messaging.Email.SendMessage(
    EmailSubject="Test Email",
    MessagePlain="Hi world!",
    Destinations=[{"EmailAddress": "recipient@example.com"}]
)

# Builder
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

**Full reference:** [docs/email.md](docs/email.md)

### Fax

```python
# Flat kwargs
response = client.Messaging.Fax.SendMessage(
    Destinations=[{"ToNumber": "+6491232345"}],
    Files=[{"Name": "Document.pdf", "Data": "<base64-encoded file data>"}]
)

# Builder
response = (
    client.Messaging.Fax
    .Set()
    .AddDestination("+6491232345")
    .AddAttachment("path/to/doc.pdf")
    .SendMessage()
)
```

**Full reference:** [docs/fax.md](docs/fax.md)

### TTS

```python
# Flat kwargs
response = client.Messaging.TTS.SendMessage(
    MessageToPeople="Hi there!",
    Destinations=[{"ToNumber": "+64211232345"}],
    Reference="Voice Test - 64211232345",
    Keypads=[{"Tone": 1, "Play": "You pressed 1", "RouteNumber": "+6491232345"}]
)

# Builder
response = (
    client.Messaging.TTS
    .Set(
        MessageToPeople="Hi there!",
        Reference="Voice Test - 64211232345"
    )
    .AddDestination("+64211232345")
    .AddKeypad(
        Tone=1,
        Play="You pressed 1",
        RouteNumber="+6491232345"
    )
    .SendMessage()
)
```

**Full reference:** [docs/tts.md](docs/tts.md)

### Voice

```python
# Flat kwargs
response = client.Messaging.Voice.SendMessage(
    MessageToPeople="path/to/audio.wav",
    MessageToAnswerPhones="path/to/audio.wav",
    Destinations=[{"ToNumber": "+64211232345"}],
    Reference="Voice Test - 64211232345",
    Keypads=[{"Tone": 1, "RouteNumber": "+6491232345"}]
)

# Builder
response = (
    client.Messaging.Voice
    .Set(
        MessageToPeople="path/to/audio.wav",
        Reference="Voice Test - 64211232345"
    )
    .AddDestination("+64211232345")
    .AddKeypad(
        Tone=1,
        RouteNumber="+6491232345"
    )
    .SendMessage()
)
```

**Full reference:** [docs/voice.md](docs/voice.md)

### WhatsApp

WhatsApp requires an approved `TemplateID` and a `FromNumber` (your registered WhatsApp sender number):

```python
# Flat kwargs
response = client.Messaging.WhatsApp.SendMessage(
    TemplateID="[Your Template ID]",
    Message="Hi there!",
    FromNumber="+6495006000",
    Destination="+64211234567"
)

# Builder
response = (
    client.Messaging.WhatsApp
    .Set(
        TemplateID="[Your Template ID]",
        Message="Hi there!",
        FromNumber="+6495006000"
    )
    .AddDestination("+64211234567")
    .SendMessage()
)
```

**Full reference:** [docs/whatsapp.md](docs/whatsapp.md)

### RCS

```python
# Flat kwargs
response = client.Messaging.RCS.SendMessage(
    Message="Hi there!",
    Destination="+64211234567"
)

# Builder
response = (
    client.Messaging.RCS
    .Set(
        Message="Hi there!"
    )
    .AddDestination("+64211234567")
    .SendMessage()
)
```

**Full reference:** [docs/rcs.md](docs/rcs.md)

### Workflow

Workflow requires a `WorkflowTemplateID` — the send is driven entirely by the template configured against your account:

```python
# Flat kwargs
response = client.Messaging.Workflow.SendMessage(
    WorkflowTemplateID="[Your Workflow Template ID]",
    Destination="+64211234567"
)

# Builder
response = (
    client.Messaging.Workflow
    .Set(
        WorkflowTemplateID="[Your Workflow Template ID]"
    )
    .AddDestination("+64211234567")
    .SendMessage()
)
```

**Full reference:** [docs/workflow.md](docs/workflow.md)

### Using Addressbook Destinations

Every channel's `AddDestination(...)` also accepts a `ContactID` or `GroupID` from your Addressbook, instead of a raw phone number/email:

```python
response = (
    client.Messaging.SMS
    .Set(
        Message="Hi [[FirstName]]"
    )
    .AddDestination(ContactID="[Contact ID]")
    .AddDestination(GroupID="[Group ID]")
    .SendMessage()
)
```

### Destination Model reference

`AddDestination(...)`, and the `Destination`/`Destinations` fields on every channel's `SendMessage(...)`,
all accept the same three shapes: a bare string (shorthand for the channel's primary field — `ToNumber`
for most channels, `EmailAddress` for Email), a plain `dict`, or a `tnzapi.core.destination.Destination`
instance. All three are equivalent — pick whichever reads best at your call site:

```python
from tnzapi.core.destination import Destination

sms = client.Messaging.SMS
sms.Set(Message="Hi [[FirstName]]!")
sms.AddDestination("+64211231234")                                 # bare string
sms.AddDestination({"ToNumber": "+64211231234", "FirstName": "Alice"})  # dict
sms.AddDestination(
    Destination(ToNumber="+64211231234", FirstName="Alice")        # typed
)
response = sms.SendMessage()
```

`Destination` is a plain `@dataclass` with every field defaulting to `None`, shared identically across
every channel:

| Field | Description |
|---|---|
| `Recipient` | Generic destination address, sent as-is regardless of channel. |
| `ToNumber` / `MobilePhone` | Phone number fields — interchangeable for SMS/WhatsApp/RCS/TTS/Voice. |
| `MainPhone` | Alternative phone field, used by TTS/Voice. |
| `EmailAddress` | Used by Email. |
| `FaxNumber` | Used by Fax. |
| `ContactID` / `GroupID` / `GroupCode` | Addressbook references — see [Using Addressbook Destinations](#using-addressbook-destinations) above. |
| `Attention` / `FirstName` / `LastName` / `Company` | Personalisation tokens, e.g. `[[FirstName]]`. |
| `Custom1`–`Custom9` | Arbitrary per-recipient personalisation values, `[[Custom1]]` … `[[Custom9]]`. |

A raw `dict` with an unrecognised key (e.g. a typo) is rejected the same way a `Destination(...)`
constructor call is — `Destination(ToNumber="...", Bogus="...")` raises `TypeError` at construction time;
an unknown dict key raises `ValueError` from `AddDestination(...)`/`Set(...)`, or is returned as
`Result="Failed"` from `SendMessage(...)`. Not every field is read by every channel — see each channel's
own doc page (e.g. [docs/sms.md](docs/sms.md)) for which Destination fields it actually uses.

`AddDestinations([...])` adds several destinations in one call, on every messaging channel - each item can
be any of the three shapes shown above (bare string, dict, or typed `Destination`), mixed freely in the
same list:

```python
sms.AddDestinations([
    "+64211231234",
    {"ToNumber": "+64211231235", "FirstName": "Alice"},
    Destination(ToNumber="+64211231236", FirstName="Bob"),
])
```

`AddDestination(...)` (singular) only ever adds one destination per call - it raises `TypeError` if given a
list directly, naming `AddDestinations(...)` as the replacement.

### File Attachment reference

`AddAttachment(...)`, and the `Files` field on Email/Fax/RCS/SMS/WhatsApp's `SendMessage(...)`, all accept
a bare file path string, a `{"Name": ..., "Data": ...}` dict, or a `tnzapi.core.file_attachment.FileAttachment`
instance - pick whichever reads best at your call site:

```python
from tnzapi.core.file_attachment import FileAttachment

fax = client.Messaging.Fax
fax.Set()
fax.AddAttachment("path/to/doc.pdf")                                # bare file path
fax.AddAttachment({"Name": "doc.pdf", "Data": "<base64>"})          # dict
fax.AddAttachment(
    FileAttachment("path/to/doc.pdf")                            # typed
)
response = fax.AddDestination("+64211231234").SendMessage()
```

A file path is read and base64-encoded automatically. **`Data` is never filesystem-checked, under any
circumstances** - `AddAttachment(Name, Data)`'s second argument and a dict's `Data` key both always store
the value exactly as given, so passing base64 content from an external source (e.g. an HTTP request body)
is always safe there, even if that content happens to coincidentally look like a real local path. Only the
explicit `FileName=`/positional-path form of `FileAttachment` (and the bare-file-path-string shorthand
shown above) ever reads from disk. Voice's audio fields (`MessageToPeople`, etc.) accept the same shapes
too - see [docs/voice.md](docs/voice.md). TTS's same-named fields are plain spoken text and are unaffected
- see [docs/tts.md](docs/tts.md).

`AddAttachments([...])` adds several attachments in one call - each item can be any shape `AddAttachment(...)`
accepts (a path string, a `{"Name": ..., "Data": ...}` dict, or a `FileAttachment` instance), e.g.
`AddAttachments(["path/to/doc.pdf", FileAttachment("path/to/other.pdf")])`.

### Send Mode reference

Every channel's `Mode` field (all except `Workflow`, which has none) accepts the typed
`tnzapi.core.send_mode.SendMode` enum as an equivalent alternative to the plain string -
`Mode=SendMode.Test`/`Mode=SendMode.Live` and `Mode="Test"`/`Mode="Live"` are fully interchangeable, since
`SendMode` is a `str`-subclass `Enum` (`SendMode.Test == "Test"` is `True`) and serializes identically over
the wire:

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

Leaving `Mode` unset is unaffected either way - it's dropped from the outgoing request body, and the server
applies its own `"Live"` default, exactly as before.

### Webhooks

**Full reference:** [docs/webhooks.md](docs/webhooks.md)

If you configure a `WebhookCallbackURL` on a send, TNZ will `POST` a status update (and, for SMS, inbound replies) back to that URL. `tnzapi.webhooks` gives you typed shapes to parse that payload in your own receiver — the SDK never sends these itself, it only documents them:

```python
from flask import Flask, request
from tnzapi.webhooks import ResultWebhookPayload, InboundSMSWebhookPayload

app = Flask(__name__)

@app.route("/webhooks/tnz/result", methods=["POST"])
def tnz_result_webhook():
    payload = ResultWebhookPayload(**request.get_json())
    print(f"{payload.MessageID} is now {payload.Status}")
    return "", 204

@app.route("/webhooks/tnz/inbound-sms", methods=["POST"])
def tnz_inbound_sms_webhook():
    payload = InboundSMSWebhookPayload(**request.get_json())
    print(f"Reply from {payload.Destination}: {payload.Message}")
    return "", 204
```

## Reports

`client.Reports` is a thin convenience wrapper, not a distinct implementation: every method here
delegates straight to the same channel-specific `Status(...)`/`Received(...)` methods reachable directly
via `client.Messaging.<Channel>` (e.g. `Reports.SMSReply.Poll(...)` internally calls
`Messaging.SMS.Status(...)`, and `Reports.SMSReceived.Poll(...)` calls `Messaging.SMS.Received(...)`) —
so the response shape and field names are exactly whatever that channel's own doc page describes (e.g.
[docs/sms.md](docs/sms.md)'s Response section for SMS), not a Reports-specific shape.

### Get Message Status

`Status.Poll(...)` routes to any of the 7 supported channels (`sms`, `email`, `fax`, `tts`, `voice`,
`whatsapp`, `rcs` — not `workflow`) by its `Channel` string, case-insensitive. An unrecognised channel
returns `Result="Failed"` with `ErrorMessage=["Unknown or unsupported channel for Status: <Channel>"]`
client-side, without making an HTTP call.

```python
response = client.Reports.Status.Poll(
    Channel="sms",
    MessageID="ID123456"
)

print(response)
```

### Get SMS Reply

SMS-specific: internally the same call as `client.Messaging.SMS.Status(MessageID)`. Inspect each entry in
the response's `Recipients` list for its `SMSReplies` field to see inbound replies attached to that
recipient — there's no separate reply-only response shape.

```python
response = client.Reports.SMSReply.Poll(
    MessageID="ID123456"
)

print(response)
```

### Get SMS Received List

SMS-specific: internally the same call as `client.Messaging.SMS.Received(...)`, for inbound SMS not tied
to a specific outbound `MessageID` (e.g. an unprompted message to your inbound number). Only ever returns
the requested page — see `samples/messaging/_pagination.py`'s `WalkAllPages` helper if you need to walk
everything.

```python
response = client.Reports.SMSReceived.Poll(
    DateFrom="2023-07-01 00:00:00",
    DateTo="2023-08-01 00:00:00"
)

print(response)
```

## Actions

Each action takes the messaging `Channel` plus the `MessageID` to act on, and routes to that channel's
own `Abort`/`Reschedule`/`Resubmit`/`Pacing` method (same one reachable directly via
`client.Messaging.<Channel>`) — not every action is supported on every channel:

| Action | Supported channels | Unsupported-channel error |
|---|---|---|
| `Abort` | `sms`, `email`, `fax`, `tts`, `voice`, `whatsapp`, `rcs` (not `workflow`) | `"Unknown or unsupported channel for Abort: <Channel>"` |
| `Reschedule` | `sms`, `email`, `fax`, `tts`, `voice`, `whatsapp`, `rcs` (not `workflow`) | `"Unknown or unsupported channel for Reschedule: <Channel>"` |
| `Resubmit` | `email`, `fax`, `tts`, `voice` only | `"Resubmit is not supported for channel: <Channel>"` |
| `Pacing` | `tts`, `voice` only | `"Pacing is not supported for channel: <Channel>"` |

The error message wording itself differs by action (`"Unknown or unsupported channel for X: ..."` vs.
`"X is not supported for channel: ..."`) — this isn't a typo to normalise, both forms are the SDK's actual
behavior; match on `Result != "Success"` rather than parsing `ErrorMessage` text if you need to detect
this case programmatically. Every action's response type (`Result`, `ErrorMessage`, plus
action-specific fields like `ActionResult`/`Status` on success) is documented on each channel's own doc
page, e.g. [docs/sms.md](docs/sms.md)'s Response section.

### Abort a Job

```python
response = client.Actions.Abort.SendRequest(
    Channel="sms",
    MessageID="ID123456"
)

print(response)
```

### Reschedule a Job

```python
response = client.Actions.Reschedule.SendRequest(
    Channel="sms",
    MessageID="ID123456",
    SendTime="2023-07-10T09:00"
)

print(response)
```

### Resubmit a Failed Job

```python
response = client.Actions.Resubmit.SendRequest(
    Channel="fax",
    MessageID="ID123456",
    SendTime="2023-07-10T09:00"
)

print(response)
```

### Adjust Pacing

```python
response = client.Actions.Pacing.SendRequest(
    Channel="tts",
    MessageID="ID123456",
    NumberOfOperators=10
)

print(response)
```

## Opt-Out Management

**Full reference:** [docs/optout.md](docs/optout.md)

Manage the do-not-contact list that TNZ checks before sending. `DestType` accepts `Fax`, `Text`, `SMS`, `Email`, `Speech` or `Voice` (comma-separated for more than one) — `SMS` and `Voice` are accepted as aliases of `Text` and `Speech` respectively.

```python
# Create a single opt-out
response = client.OptOut.Create(
    DestType="SMS",
    Destination="+64211234567",
    Notes="Requested via support call"
)

# Create a batch of opt-outs in one call
response = client.OptOut.CreateBatch(
    DestType="SMS,Email",
    Destinations=["+64211234567", "+64221234567"]
)

# List opt-outs, optionally filtered by time period / dest type / contact
response = client.OptOut.List(
    DestType="SMS",
    RecordsPerPage=20,
    Page=1
)

# Get details of one opt-out
response = client.OptOut.Details("[Opt-Out ID]")

# Update an opt-out (partial - only supplied fields are changed)
response = client.OptOut.Update("[Opt-Out ID]", Notes="Updated notes")

# Delete an opt-out
response = client.OptOut.Delete("[Opt-Out ID]")

# Update/Delete using a Response you already have (e.g. from Details()) -
# only the fields Update() actually accepts are sent (read-only fields like
# ID/timestamps are dropped automatically), and the ID itself can come
# straight from the Response too
details_result = client.OptOut.Details("[Opt-Out ID]")
details_result.Notes = "Updated notes"
response = client.OptOut.Update(details_result, model=details_result)
response = client.OptOut.Delete(details_result)

print(response)
```

## Addressbook

**Full reference:** [docs/addressbook.md](docs/addressbook.md)

### Contacts

```python
# List
response = client.Addressbook.Contact.List(RecordsPerPage=10, Page=1)

# Search
response = client.Addressbook.Contact.Search(Attention="Joe", RecordsPerPage=10, Page=1)

# Detail
response = client.Addressbook.Contact.Detail("[Contact ID]")

# Create
response = client.Addressbook.Contact.Create(
    Title="Mr",
    Company="TNZ Group",
    FirstName="First",
    LastName="Last",
    MobilePhone="+642122223333"
)

# Update
response = client.Addressbook.Contact.Update("[Contact ID]", Attention="Test Attention")

# Delete
response = client.Addressbook.Contact.Delete("[Contact ID]")

# Update/Delete using a Response you already have (e.g. from Detail()) -
# only the fields Update() actually accepts are sent (read-only fields like
# ContactID/Owner/timestamps are dropped automatically), and the ID itself
# can come straight from the Response too
detail_result = client.Addressbook.Contact.Detail("[Contact ID]")
detail_result.Attention = "Test Attention"
response = client.Addressbook.Contact.Update(detail_result, model=detail_result)
response = client.Addressbook.Contact.Delete(detail_result)

print(response)
```

### Groups

```python
# List
response = client.Addressbook.Group.List(RecordsPerPage=10, Page=1)

# Detail
response = client.Addressbook.Group.Detail("[Group ID]")

# Create
response = client.Addressbook.Group.Create(GroupName="[Group Name]")

# Update
response = client.Addressbook.Group.Update("[Group ID]", GroupName="[New Group Name]")

# Delete
response = client.Addressbook.Group.Delete("[Group ID]")

# Update/Delete using a Response you already have (e.g. from Detail()) -
# only the fields Update() actually accepts are sent (read-only fields like
# GroupID/Owner/timestamps are dropped automatically), and the ID itself
# can come straight from the Response too
detail_result = client.Addressbook.Group.Detail("[Group ID]")
detail_result.GroupName = "[New Group Name]"
response = client.Addressbook.Group.Update(detail_result, model=detail_result)
response = client.Addressbook.Group.Delete(detail_result)

print(response)
```

### Contact Groups

Manage which groups a contact belongs to:

```python
# List the groups a contact belongs to
response = client.Addressbook.ContactGroup.List("[Contact ID]", RecordsPerPage=10, Page=1)

# Detail of one contact/group membership
response = client.Addressbook.ContactGroup.Detail("[Contact ID]", "[Group ID]")

# Add a contact to a group
response = client.Addressbook.ContactGroup.Create("[Contact ID]", "[Group ID]")

# Remove a contact from a group
response = client.Addressbook.ContactGroup.Delete("[Contact ID]", "[Group ID]")

print(response)
```

### Group Contacts

The same relationship viewed from the group's side:

```python
# List the contacts belonging to a group
response = client.Addressbook.GroupContact.List("[Group ID]", RecordsPerPage=10, Page=1)

# Detail of one group/contact membership
response = client.Addressbook.GroupContact.Detail("[Group ID]", "[Contact ID]")

# Add a contact to a group
response = client.Addressbook.GroupContact.Create("[Group ID]", "[Contact ID]")

# Remove a contact from a group
response = client.Addressbook.GroupContact.Delete("[Group ID]", "[Contact ID]")

print(response)
```

`List()` results only cover the requested page — this SDK never auto-walks every page on your behalf. Inspect `PageCount`/`TotalRecords` on the response and request further pages yourself if you need them.

## Legacy API Support

Code written against the pre-2.0.3 method-call API (`client.Send.SMS(...)`, `client.Get.Status(...)`, `client.Set.Pacing(...)`) is still fully supported — it isn't deprecated and isn't being removed. `.Send`, `.Get` and `.Set` continue to wrap the older v2.04 REST API under the hood (rather than v3.00), and can be authenticated with either `AuthToken` or the legacy `Sender`/`APIKey` pair:

```python
from tnzapi import TNZAPI

client = TNZAPI(
    Sender="[Your Sender]",
    APIKey="[Your API Key]"
)

response = client.Send.SMS(
    Recipients=["+64211231234"],
    MessageText="Hi there!"
).SendMessage()

print(response)
```

If you're maintaining an existing integration built on this style, there's no need to migrate it to `.Messaging`/`.Reports`/`.Actions` — both styles are supported side by side on the same `TNZAPI` client and will keep working.

## Response Structure

Every response object (from `.Messaging`, `.Reports`, `.Actions`, `.Addressbook` and `.OptOut`) exposes at least:

- `.Result` — `"Success"` on success, otherwise a failure code such as `"Failed"`, `"Unauthorized"` or `"RecordNotFound"`.
- `.ErrorMessage` — a list of human-readable error strings, populated whenever `.Result != "Success"`.

Successful responses additionally expose the fields relevant to that call (e.g. `.MessageID` on a send, `.ContactID` on a contact create/detail, `.OptOuts` on an opt-out list).

If you want to type-hint against a response's class (e.g. in a function signature), import it from `tnzapi.models` rather than the internal `tnzapi.api.v300....models.responses...` module path:

```python
from tnzapi.models import SMSResponse

def handle(result: SMSResponse) -> None:
    ...
```

`tnzapi.models` re-exports every response type across `.Messaging`/`.Reports`/`.Actions`/`.Addressbook`/`.OptOut` under its plain name (`SMSResponse`, `ContactResponse`, `OptOutListResponse`, etc.) — these were named with a `...DTO` suffix in earlier versions, which still works via a `DeprecationWarning`-emitting alias.

### `Recipients`/`Messages` are plain dicts, except SMS

Every channel's `Status(...)`/`Received(...)` response carries a list of per-recipient/per-message
entries (`Recipients`, `Messages`, or similar). On every channel **except SMS**, these are plain `dict`
objects — access fields with `entry.get("Field")` or `entry["Field"]`, not attribute access.
**SMS is the one exception**: its `Recipients` list holds typed `SMSRecipient` objects (with a nested
`SMSReply` type for inbound replies), so `entry.Field` works there. This asymmetry is deliberate, not an
oversight — SMS was the first channel to get typed response objects; the rest still use plain dicts. Each
channel's own doc page under [docs/](docs/messaging.md) states which shape applies.

### Common response enums

- **`JobStatus`** (on every channel's `Status(...)` response): `"Pending"`, `"Delayed"`, `"Completed"`,
  `"CreditHold"`, `"Unknown"`.
- **Per-recipient `Status`** (inside `Recipients`/`Messages` entries): `"Success"`, `"Failed"`, `"Pending"`.
- **Per-recipient `Type`** (inside `Recipients`/`Messages` entries): the channel that actually delivered
  this recipient, not necessarily the channel you called — relevant when `FallbackMode` triggers.
  **TTS and Voice both report `Type="Voice"`** — there's no separate `"TTS"` value on the wire, since the
  underlying delivery mechanism is identical for both from the TNZ API's point of view.

### ID-validation guards

Every method that takes a required, standalone ID parameter (e.g. `MessageID` on `Status(...)`,
`ContactID`/`GroupID` on `Detail(...)`/`Update(...)`/`Delete(...)`, `OptOutID` on `OptOut.Details(...)`)
raises `ValueError` immediately if you pass `None` or `""` — rather than silently building a broken
request URL like `.../contact/None` or comparing an unset ID in memory. `Update(...)`/`Delete(...)`
methods that also accept a Response object in place of a plain ID string raise the same `ValueError` if
that Response's ID field itself isn't set (e.g. it came from a failed prior call). This is a client-side
guard — no HTTP request is made when it fires.

## Error Handling

```python
result = client.Messaging.SMS.SendMessage(
    Message="Hi there!",
    Destination="+64211231234"
)

if result.Result != "Success":
    print(result.ErrorMessage)
else:
    print(result.MessageID)
```

## Development & Testing

```bash
# Install in editable mode with test dependencies
pip install -e .[test]

# Run the test suite
pytest
```

Tests load configuration via `python-dotenv`, layered in this order (later files override earlier ones): `.env`, then `.env.local`, then `.env.test`. Unit tests are hermetic by default — a fixture clears `TNZ_API_URL`/`TNZ_AUTH_TOKEN`/`TNZ_ALLOW_INSECURE_HTTP` from the environment before each test, so a developer's local `.env`/`.env.local` (e.g. pointing at a local test server) never leaks into a test unless that test explicitly opts in.

### Integration tests

`tests/integration/` hits a real TNZ API instance instead of mocking the HTTP layer — it's excluded from a plain `pytest` run (`pytest.ini`'s `addopts = -m "not integration"`) and only runs when asked for explicitly:

```bash
pytest -m integration
```

Copy `.env.test.example` to `.env.test` and fill in real values first — each test skips gracefully if the environment variables it needs aren't set. Messaging-send tests pass `Mode="Test"` on every channel that supports it (all except `Workflow`) on the assumption it's a no-cost/no-delivery switch; this hasn't been confirmed against production, so treat a real send/charge as a live possibility until verified.

Beyond having `TNZ_AUTH_TOKEN` configured, running any live test also requires `TNZ_RUN_LIVE_TESTS=1` — a deliberate second confirmation, since a real token being present isn't itself permission to fire real (possibly billable) requests. The `Workflow` send test needs a further `TNZ_ALLOW_WORKFLOW_SEND=1`, since `Workflow` has no `Mode="Test"` equivalent and the configured `TNZ_TEST_WORKFLOW_TEMPLATE_ID` genuinely executes on every run. `WhatsApp`/`RCS` send tests skip (rather than fail) on a `Failed` result, since that can mean the account isn't provisioned for that channel rather than an SDK regression.

## Getting Help

If you need help installing or using the library, please check the [TNZ Contact](https://www.tnz.co.nz/About/Contact/) if you don't find an answer to your question.

[apidocs]: https://www.tnz.co.nz/Docs/PythonLib/