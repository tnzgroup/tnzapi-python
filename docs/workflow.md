# Workflow

Trigger a pre-configured, no-code Workflow Template (built via the TNZ Dashboard) rather than sending a single-channel message directly. A Workflow Template can span multiple channels and automation steps on its own, so the send itself carries no message content — just a template reference and destinations. Workflow is structurally different from every other messaging module: it has only `SendMessage` — no `Status`, no `Received`, and no `Reschedule`/`Abort`/`Resubmit`/`Pacing`.

→ [Common parameters & authentication](../README.md#messaging)

## Quick example

Workflow destinations are genuinely omni-channel: unlike every other module (where a destination targets exactly one address type), a single `Destinations` entry can carry `ToNumber`, `MainPhone`, and `EmailAddress` all at once — the Workflow Template itself decides which channel(s) actually get used for that recipient.

```python
from tnzapi import TNZAPI

client = TNZAPI(AuthToken="[Your Auth Token]")

response = client.Messaging.Workflow.SendMessage(
    WorkflowTemplateID="[Your Workflow Template ID]",
    Destination="+64211234567"
)

if response.Result == "Success":
    print(f"Success - MessageID: {response.MessageID}")
```

## Parameters (`WorkflowRequest`)

| Parameter | Type | Required | Description |
|---|---|---|---|
| `WorkflowTemplateID` | `str` | Yes | ID of the Workflow Template to trigger, as configured in the TNZ Dashboard. |
| `Destination` | `str` | Cond.† | Single destination shorthand, e.g. `"+64211234567"`. |
| `ToNumber` | `str` | Cond.† | Alternative single-destination field (phone number). |
| `MainPhone` | `str` | Cond.† | Alternative single-destination field for a secondary/main phone number, distinct from `ToNumber`. |
| `Destinations` | `list[dict]` | Cond.† | One or more destinations — see Destination fields below. |
| `ContactID` | `str` | No | Single addressbook contact to send to (alternative/addition to `Destinations`). |
| `GroupID` | `str` | No | Single addressbook group to send to (alternative/addition to `Destinations`). |
| `MessageID` | `str` | No | Supply your own message ID (otherwise auto-generated). |
| `Reference` | `str` | No | Your internal reference, returned in reports and webhooks. |
| `NotificationType` | `str` | No | Notification delivery mode. |
| `WebhookCallbackURL` | `str` | No | URL for delivery status callbacks. |
| `WebhookCallbackFormat` | `str` | No | Callback format (`JSON`/`XML`/`POST`/`GET`). |
| `SubAccount` | `str` | No | Sub-account code for billing separation. |
| `Department` | `str` | No | Department code. |
| `SendTime` | `str` | No | Schedule delivery — combine with `Timezone`. |
| `Timezone` | `str` | No | Timezone name for `SendTime` (e.g. `"New Zealand"`, `"Pacific/Auckland"`). |

†`SendMessage(...)` checks this client-side, before even checking `WorkflowTemplateID`: if none of `Destinations`/`Destination`/`ToNumber` is set, it immediately returns `Result="Failed"` with `ErrorMessage=["Missing required field: Destinations, Destination, or ToNumber"]`, without contacting the TNZ API at all. Passing `MainPhone`, `ContactID`, or `GroupID` alone as a top-level `SendMessage(...)` keyword argument does **not** satisfy this check — route those through `Destinations` or `AddDestination(...)` instead. Unlike every other channel, Workflow has no `Message`/`TemplateID` text-content field, no attachments (`Files`), no `ReportTo`, and no `Mode` (there is no "Test" send mode — every Workflow send is live).

## Destination fields (`Destinations` list items)

| Field | Description |
|---|---|
| `ToNumber` | Destination phone number, e.g. `"+64211111111"`. |
| `MainPhone` | Secondary/main phone number — a separate wire field from `ToNumber`, letting the Workflow Template distinguish the two. Can be set **alongside** `ToNumber` and `EmailAddress` on the same entry. |
| `MobilePhone` | Alternative phone field — can also be set alongside `MainPhone`/`ToNumber` on the same entry. |
| `FaxNumber` | Destination fax number — can also be set alongside the other address fields on the same entry. |
| `EmailAddress` | Destination email address. Can be set **alongside** `ToNumber`/`MainPhone` on the same entry — this is what makes a Workflow destination omni-channel. |
| `Recipient` | Generic destination address, sent as-is regardless of channel. |
| `ContactID` | Addressbook contact reference — sends to that contact instead of raw addresses. |
| `GroupID` | Addressbook group reference — sends to all members of that group. |
| `GroupCode` | Alternative group lookup by code (instead of `GroupID`). |
| `FirstName` / `LastName` / `Company` / `Attention` | Personalisation values, passed through to whichever channel(s) the Workflow Template actually uses. |
| `Custom1`–`Custom9` | Arbitrary per-recipient personalisation values. |

If a destination isn't a known `ContactID`/`GroupID`, the API automatically creates (or updates) an Addressbook contact from whichever address/personalisation fields you supply alongside it.

A `tnzapi.core.destination.Destination` instance can be used instead of a raw dict — it validates
field names at construction time (`Destination(ToNumber="...", Bogus="...")` raises `TypeError`),
and an unknown key in a raw dict is now rejected the same way (`ValueError` for `Set()`/
`AddDestination()`, `Result="Failed"` for `SendMessage()`).

## Code samples

### Flat kwargs

```python
response = client.Messaging.Workflow.SendMessage(
    WorkflowTemplateID="[Your Workflow Template ID]",
    Destination="+64211234567"
)
```

### Builder

```python
response = (
    client.Messaging.Workflow
    .Set(
        WorkflowTemplateID="[Your Workflow Template ID]"
    )
    .AddDestination("+64211234567")
    .SendMessage()
)
```

### Addressbook destination

```python
response = (
    client.Messaging.Workflow
    .Set(
        WorkflowTemplateID="[Your Workflow Template ID]"
    )
    .AddDestination(ContactID="[Contact ID]")
    .AddDestination(GroupID="[Group ID]")
    .SendMessage()
)
```

### Multiple recipients

```python
response = client.Messaging.Workflow.SendMessage(
    WorkflowTemplateID="[Your Workflow Template ID]",
    Destinations=[
        {"ToNumber": "+64211234567"},
        {"ToNumber": "+64211234568"},
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
    client.Messaging.Workflow
    .Set(WorkflowTemplateID="[Your Workflow Template ID]")
    .AddDestinations(["+64211234567", "+64211234568"])
    .SendMessage()
)
```

### Bulk send with per-destination personalisation, via `AddDestinations`

Personalisation fields on each destination are passed through to whichever channel(s) the Workflow
Template actually routes to.

```python
from tnzapi.core.destination import Destination

response = (
    client.Messaging.Workflow
    .Set(WorkflowTemplateID="[Your Workflow Template ID]")
    .AddDestinations([
        Destination(
            ToNumber="+64211234567",
            FirstName="Alice",
            Company="Example Company",
        ),
        Destination(
            ToNumber="+64211234568",
            FirstName="Bob",
            Company="Example Company",
        ),
    ])
    .SendMessage()
)
```

### Omni-channel destination

```python
response = client.Messaging.Workflow.SendMessage(
    WorkflowTemplateID="[Your Workflow Template ID]",
    Destinations=[{
        "ToNumber": "+6421000001",
        "MainPhone": "+6421000001",
        "EmailAddress": "john.doe@example.com",
        "Attention": "John Doe",
        "FirstName": "John",
        "LastName": "Doe",
        "Company": "Example Company",
    }],
)
```

### Scheduled send

```python
response = client.Messaging.Workflow.SendMessage(
    WorkflowTemplateID="[Your Workflow Template ID]",
    Destination="+64211234567",
    SendTime="2026-08-01T09:00:00",
    Timezone="Pacific/Auckland",
)
```

## Response

- `SendMessage(...)` → `WorkflowResponse`: `Result`, `MessageID`, `ErrorMessage`.

`WorkflowResponse` was named `WorkflowResponseDTO` before this SDK's public response types dropped that internal-architecture suffix; the old name still works (it emits a `DeprecationWarning`) — see [messaging.md](messaging.md#response-shape).

Workflow has no `Status`, `Received`, or Action (`Reschedule`/`Abort`/`Resubmit`/`Pacing`) methods — the request class exposes `SendMessage` only.

## See also

- [README — Workflow](../README.md#workflow)
- [Samples — workflow_samples.py](../samples/messaging/workflow_samples.py)
