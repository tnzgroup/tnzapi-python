# Inbound Webhooks

TNZ's webhooks notify your application when a message completes sending, or when you receive an inbound
SMS, instead of you polling `Status(...)`/`Received(...)` on a timer. This keeps delivery receipts and
customer replies flowing to your system without the extra request load that polling adds.

Webhooks are **inbound**: TNZ's servers POST these payloads *to your own server* (configure
`WebhookCallbackURL` on a send, or your Sender's Dashboard settings for SMS-reply/result reporting). The
SDK doesn't call anything for this; instead, `tnzapi.webhooks` provides typed dataclass shapes you can
construct from an incoming request body in your own webhook receiver endpoint.

→ [Common parameters & authentication](../README.md#messaging)

**Security note:** TNZ does not sign or otherwise authenticate these POSTs — no HMAC or shared-secret
header is provided. Anyone who discovers your `WebhookCallbackURL` can post a payload to it. Don't expose
a receiver like the ones below on a public route without adding your own verification, e.g. a random,
hard-to-guess path segment or query token, an IP allowlist for TNZ's sending range, or routing the
callback through your own authenticated proxy.

## Payload fields

`ResultWebhookPayload` and `InboundSMSWebhookPayload` share the exact same field set, both dataclasses
subclassing a shared private base. Every field on both classes is a plain `str`, defaulting to `None`.
They're kept as two distinct classes purely so a receiver's type hints communicate which kind of event
it's handling, even though the wire shape happens to be identical today.

| Field | Type | Description |
|---|---|---|
| `Version` | `str` | Webhook payload format version. |
| `Sender` | `str` | Your TNZ Sender ID. |
| `APIKey` | `str` | Your API key, included for correlation/validation. |
| `Type` | `str` | Message channel type (e.g. `"SMS"`). |
| `Destination` | `str` | The recipient (or, for inbound SMS, the sender) address/number. |
| `ContactID` | `str` | Addressbook contact reference, if the destination matched one. |
| `ReceivedID` | `str` | Identifier for this specific inbound/result event. |
| `MessageID` | `str` | The original outbound message this event relates to. |
| `SubAccount` | `str` | Sub-account code, echoed from the original send. |
| `Department` | `str` | Department code, echoed from the original send. |
| `JobNumber` | `str` | Job number for the send batch. |
| `SentTimeLocal` / `SendTimeUTC` / `SentTimeUTC_RFC3339` | `str` | Event timestamp in local time, UTC, and RFC3339 UTC respectively. Note the middle field is named `SendTimeUTC`, not `SentTimeUTC` (a real inconsistency versus its `SentTime*` neighbours), reproduced here exactly as the SDK defines it. |
| `Status` | `str` | Delivery/message status. |
| `Result` | `str` | Result code/description for this event. |
| `Message` | `str` | The message text (the reply body for inbound SMS). |
| `Price` | `str` | See the [Price note below](#a-note-on-price). |
| `Detail` | `str` | Additional detail text for this event. |
| `URL` | `str` | Related URL, if applicable. |

Both classes are plain `@dataclass`es with no tolerance for unexpected keys: constructing one from a
payload that includes a field neither class declares raises `TypeError`, unlike the tolerant
field-by-field parsing this SDK's own HTTP responses go through internally. If TNZ ever adds a new field
to the wire payload before this SDK is updated to match, filter the parsed body down to known keys
yourself before constructing the dataclass, e.g.
`{k: v for k, v in body.items() if k in ResultWebhookPayload.__dataclass_fields__}`.

## Code samples

### Delivery result webhook

Handle the payload TNZ posts when a message completes sending, whatever the outcome, as an alternative to
polling `Status(...)`. `RequestBody` is the already-JSON-decoded body your web framework gave you, e.g.
Flask's `request.get_json()` or Django's `json.loads(request.body)`.

```python
from tnzapi.webhooks import ResultWebhookPayload

payload = ResultWebhookPayload(**RequestBody)

print(f"{payload.Type} to {payload.Destination}: {payload.Status} ({payload.Result})")
```

### Inbound SMS webhook

Handle the payload TNZ posts when a recipient replies to an SMS, as an alternative to polling
`Received(...)`.

```python
from tnzapi.webhooks import InboundSMSWebhookPayload

payload = InboundSMSWebhookPayload(**RequestBody)

print(f"Inbound SMS from {payload.Destination}: {payload.Message}")
```

### Flask receiver example

Wiring both payload types into two routes of a small Flask app. This SDK has no Flask dependency itself;
any framework that hands you the parsed JSON body works the same way.

```python
from flask import Flask, request
from tnzapi.webhooks import ResultWebhookPayload, InboundSMSWebhookPayload

app = Flask(__name__)


@app.route("/webhooks/tnz/result", methods=["POST"])
def tnz_result_webhook():
    body = request.get_json(silent=True)
    if body is None:
        return "", 400
    payload = ResultWebhookPayload(**body)
    print(f"{payload.MessageID} is now {payload.Status}")
    return "", 204


@app.route("/webhooks/tnz/inbound-sms", methods=["POST"])
def tnz_inbound_sms_webhook():
    body = request.get_json(silent=True)
    if body is None:
        return "", 400
    payload = InboundSMSWebhookPayload(**body)
    print(f"Reply from {payload.Destination}: {payload.Message}")
    return "", 204
```

### A note on `Price`

`Price` is annotated `str` on both payload types, but `ResultWebhookPayload`/`InboundSMSWebhookPayload`
are plain `@dataclass`es with no validation or type coercion: the annotation is a type hint only, not
enforced at runtime. TNZ's webhook callback may send `Price` as either a JSON string or a JSON number; if
it arrives as a number, `payload.Price` will actually hold an `int`/`float` at runtime despite the
annotation, since `ResultWebhookPayload(**body)` assigns whatever value `body["Price"]` is verbatim.
Normalise it explicitly if you need a consistent type, e.g. `Decimal(str(payload.Price))`.

## See also

- [README — Webhooks](../README.md#webhooks)
- [Samples — webhook_samples.py](../samples/webhooks/webhook_samples.py)
