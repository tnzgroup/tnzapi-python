"""Inbound webhook parsing sample code. Full reference: README.md > Messaging > Webhooks.

If you configure a WebhookCallbackURL on a send, TNZ will POST a status
update (and, for SMS, inbound replies) back to that URL. This SDK never
sends these payloads itself - tnzapi.webhooks only gives you typed shapes
to parse them in your own receiver.

TNZ does not sign or otherwise authenticate these POSTs (no HMAC/shared-secret
header is provided), so anyone who discovers your WebhookCallbackURL can post
a payload to it. Don't deploy a receiver like the one below as-is on a public
route without adding your own verification - e.g. a random, hard-to-guess path
segment or query token, an IP allowlist for TNZ's sending range, or routing
the callback through your own authenticated proxy.
"""

from tnzapi.webhooks import ResultWebhookPayload, InboundSMSWebhookPayload


class WebhookSamples:

    def ParseResultWebhook(self, RequestBody: dict) -> ResultWebhookPayload:
        """RequestBody is the already-JSON-decoded body your web framework gave you
        (e.g. Flask's request.get_json(), Django's json.loads(request.body))."""
        payload = ResultWebhookPayload(**RequestBody)
        print(f"{payload.Type} to {payload.Destination}: {payload.Status} ({payload.Result})")
        print(f"    -> MessageID: {payload.MessageID}")
        print(f"    -> SentTimeLocal: {payload.SentTimeLocal}")
        return payload

    def ParseInboundSMSWebhook(self, RequestBody: dict) -> InboundSMSWebhookPayload:
        payload = InboundSMSWebhookPayload(**RequestBody)
        print(f"Inbound SMS from {payload.Destination}: {payload.Message}")
        print(f"    -> Type: {payload.Type}")
        print(f"    -> ReceivedID: {payload.ReceivedID}")
        return payload

    def FlaskReceiverExample(self):
        """Illustrative only - shows how to wire the two parse methods above
        into a Flask app. Returns the source as a string rather than executing
        it, since this class itself has no Flask dependency."""
        return '''
from flask import Flask, request
from samples.webhooks.webhook_samples import WebhookSamples

app = Flask(__name__)
samples = WebhookSamples()

@app.route("/webhooks/tnz/result", methods=["POST"])
def tnz_result_webhook():
    samples.ParseResultWebhook(request.get_json())
    return "", 204

@app.route("/webhooks/tnz/inbound-sms", methods=["POST"])
def tnz_inbound_sms_webhook():
    samples.ParseInboundSMSWebhook(request.get_json())
    return "", 204
'''
